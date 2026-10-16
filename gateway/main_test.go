package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestGateway(t *testing.T) {
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer valid" {
			w.WriteHeader(401)
			return
		}
		if r.URL.Path == "/api/v1/auth/me" {
			w.Write([]byte(`{"user_id":"owned"}`))
			return
		}
		if r.Header.Get("X-User-ID") != "" {
			t.Error("spoofed identity forwarded")
		}
		w.Write([]byte(`{"same_task":true}`))
	}))
	defer upstream.Close()
	handler := gateway(upstream.URL)
	for _, tc := range []struct {
		path, token string
		want        int
	}{{"/api/v1/tasks", "", 401}, {"/api/v1/tasks", "Bearer valid", 200}, {"/other", "Bearer valid", 404}, {"/health/live", "", 200}} {
		r := httptest.NewRequest("GET", tc.path, nil)
		r.Header.Set("Authorization", tc.token)
		r.Header.Set("X-User-ID", "forged")
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, r)
		if w.Code != tc.want {
			t.Fatalf("got %d want %d", w.Code, tc.want)
		}
	}
	r := httptest.NewRequest("POST", "/api/v1/tasks", strings.NewReader(strings.Repeat("x", 2_000_001)))
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, r)
	if w.Code != 413 {
		t.Fatal(w.Code)
	}
}
func TestRateLimit(t *testing.T) {
	l := limiter{clients: map[string]entry{}}
	for i := 0; i < 120; i++ {
		if !l.allow("device") {
			t.Fatal(i)
		}
	}
	if l.allow("device") {
		t.Fatal("no limit")
	}
}
