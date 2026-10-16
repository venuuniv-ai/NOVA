package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

type entry struct {
	count int
	start time.Time
}
type limiter struct {
	sync.Mutex
	clients map[string]entry
	maximum int
}

func (l *limiter) allow(id string) bool {
	l.Lock()
	defer l.Unlock()
	now := time.Now()
	e := l.clients[id]
	if now.Sub(e.start) > time.Minute {
		e = entry{start: now}
	}
	if len(l.clients) > 4096 {
		for k, v := range l.clients {
			if now.Sub(v.start) > time.Minute {
				delete(l.clients, k)
			}
		}
		if len(l.clients) > 4096 {
			return false
		}
	}
	e.count++
	l.clients[id] = e
	maximum := l.maximum
	if maximum == 0 {
		maximum = 120
	}
	return e.count <= maximum
}

var correlation = regexp.MustCompile(`^[A-Za-z0-9._:-]{1,64}$`)

func gateway(base string) http.Handler {
	target, err := url.Parse(base)
	if err != nil || target.Scheme != "http" || target.Host == "" || target.User != nil || target.RawQuery != "" || target.Path != "" {
		panic("invalid internal backend URL")
	}
	client := &http.Client{Timeout: 3 * time.Second, CheckRedirect: func(req *http.Request, via []*http.Request) error { return http.ErrUseLastResponse }, Transport: &http.Transport{Proxy: nil}}
	maximum, _ := strconv.Atoi(os.Getenv("REQUESTS_PER_MINUTE"))
	if maximum < 1 || maximum > 10000 {
		maximum = 1200
	}
	limits := &limiter{clients: make(map[string]entry), maximum: maximum}
	identities := &limiter{clients: make(map[string]entry), maximum: maximum}
	proxy := httputil.NewSingleHostReverseProxy(target)
	proxy.Transport = &http.Transport{Proxy: nil, ResponseHeaderTimeout: 12 * time.Second}
	original := proxy.Director
	proxy.Director = func(r *http.Request) {
		original(r)
		r.Header.Del("Cookie")
		r.Header.Del("X-User-ID")
		r.Header.Del("X-Roles")
		r.Header.Del("X-Device-ID")
		r.Header.Del("Forwarded")
		r.Header.Del("X-Forwarded-Host")
		r.Header.Del("X-Forwarded-Proto")
	}
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		http.Error(w, `{"error":{"code":"UPSTREAM_UNAVAILABLE"}}`, 503)
	}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Cache-Control", "no-store")
		if r.URL.Path == "/health/live" {
			w.Write([]byte(`{"status":"alive"}`))
			return
		}
		if !strings.HasPrefix(r.URL.Path, "/api/v1/") {
			http.NotFound(w, r)
			return
		}
		if r.Method != "GET" && r.Method != "POST" && r.Method != "DELETE" {
			w.WriteHeader(405)
			return
		}
		host, _, _ := net.SplitHostPort(r.RemoteAddr)
		if !limits.allow(host) {
			w.WriteHeader(429)
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, 2_000_000)
		if r.ContentLength > 2_000_000 {
			w.WriteHeader(413)
			return
		}
		id := r.Header.Get("X-Correlation-ID")
		if !correlation.MatchString(id) {
			id = time.Now().UTC().Format("20060102T150405.000000000")
		}
		r.Header.Set("X-Correlation-ID", id)
		w.Header().Set("X-Correlation-ID", id)
		ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
		defer cancel()
		r = r.WithContext(ctx)
		check, _ := http.NewRequestWithContext(ctx, "GET", base+"/api/v1/auth/me", nil)
		check.Header.Set("Authorization", r.Header.Get("Authorization"))
		response, err := client.Do(check)
		if err != nil {
			w.WriteHeader(503)
			return
		}
		defer response.Body.Close()
		if response.StatusCode != 200 {
			w.WriteHeader(response.StatusCode)
			return
		}
		var identity struct {
			UserID   string `json:"user_id"`
			DeviceID string `json:"device_id"`
		}
		if json.NewDecoder(http.MaxBytesReader(w, response.Body, 10000)).Decode(&identity) != nil || identity.UserID == "" {
			w.WriteHeader(502)
			return
		}
		if !identities.allow(identity.UserID + ":" + identity.DeviceID) {
			w.WriteHeader(429)
			return
		}
		// FastAPI re-verifies the original bearer and owns every resource/policy decision.
		proxy.ServeHTTP(w, r)
	})
}
func main() {
	base := os.Getenv("BACKEND_URL")
	if base == "" {
		base = "http://backend:8000"
	}
	slog.Info("gateway_start", "auth_authority", "fastapi")
	server := &http.Server{Addr: ":8080", Handler: gateway(base), ReadHeaderTimeout: 3 * time.Second, ReadTimeout: 15 * time.Second, WriteTimeout: 20 * time.Second, IdleTimeout: 30 * time.Second, MaxHeaderBytes: 16384}
	if err := server.ListenAndServe(); err != nil {
		slog.Error("gateway_stopped")
		os.Exit(1)
	}
}
