FROM golang:1.25-alpine AS build
RUN apk add --no-cache build-base
WORKDIR /src
COPY go.mod .
COPY *.go .
RUN gofmt -w *.go && go test -race ./... && go build -trimpath -o /gateway .
FROM alpine:3.22
RUN addgroup -S nova && adduser -S -G nova nova
COPY --from=build /gateway /gateway
USER nova
EXPOSE 8080
ENTRYPOINT ["/gateway"]
