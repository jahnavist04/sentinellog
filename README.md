# SentinelLog

A distributed logging and monitoring system built to understand how real-time log aggregation works at scale.

Three independent services generate logs simultaneously. A central collector receives them via persistent socket connections, validates them, and stores them in PostgreSQL. A Flask API exposes the data. A React dashboard visualizes everything in real time.

The entire stack runs with one command.

## Architecture

ServiceA ──→

ServiceB ──→  Collector (TCP sockets) ──→ PostgreSQL ──→ Flask API ──→ React Dashboard

ServiceC ──→

## Stack

- **Services** — Python, simulating distributed network nodes
- **Collector** — Python socket server with threading
- **Database** — PostgreSQL
- **API** — Flask + REST
- **Frontend** — React + Recharts
- **Containerization** — Docker + docker-compose
- **CI/CD** — GitHub Actions

## Features

- Real-time log aggregation from multiple services simultaneously
- Live dashboard with auto-refresh every 2 seconds
- Search logs by keyword
- Filter by log level (INFO / WARNING / ERROR)
- Filter by service
- Bar chart showing log distribution per service
- High error rate alerts
- Export logs as CSV
- Retry mechanism for container startup race conditions
- GitHub Actions CI pipeline

## Run locally

```bash
git clone https://github.com/jahnavist04/sentinellog.git
cd sentinellog
docker compose up --build
```

Open `http://localhost:3000` in your browser.

## Why I built this

I wanted to understand how tools like ELK Stack and Datadog work under the hood — not just use them. Building the collector, storage layer, API, and dashboard from scratch gave me a real understanding of distributed systems architecture.

In a production environment, the three Python services would be replaced by real network nodes or microservices running on separate machines.

---

Built by Jahnavi S T · [LinkedIn](https://www.linkedin.com/in/jahnavi-s-t/) · [GitHub](https://github.com/jahnavist04)