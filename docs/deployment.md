# Deployment & Operations Guide

## 1. Quick Start via Docker Compose

The complete system (PostgreSQL, FastAPI Backend, React Frontend, and Scheduler Worker) can be spun up in one command:

```bash
docker compose up --build -d
```

### Services & Port Mapping
- **Frontend Dashboard**: `http://localhost:5173` (or `http://localhost:80`)
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **PostgreSQL Database**: `localhost:5432` (`user: postgres`, `password: postgres`, `db: priceintel`)

To monitor logs:
```bash
docker compose logs -f backend scheduler
```

To stop all services:
```bash
docker compose down
```

---

Compose binds the published ports to loopback and uses demo credentials. The backend seeds an empty catalog and the scheduler waits for the backend health check before starting.

## 2. Local Development Setup (Without Docker)

Run the shell blocks from the project root in separate terminals. Use a disposable database when running the seed script, which resets existing records by default.

### Backend
```bash
python -m pip install -r backend/requirements.txt

# Seed reproducible demo catalog (500 products, 3 retailers, 90-day history)
python scripts/seed_demo.py

# Start API server
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm ci
npm run dev
```

### Run Tests
```bash
cd backend
python -m pytest tests/ -v
```
