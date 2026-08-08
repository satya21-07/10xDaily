# 10xDaily 🚀

> "Become 1% Smarter Every Day."

10xDaily is a full-stack, production-grade learning operating system designed to deliver high-quality, bite-sized lessons across various domains including Vocabulary, Tech/AI News, Coding, Finance, Health, and Spirituality.

## Architecture & Tech Stack

This project strictly adheres to Clean Architecture principles.

### Backend 🐍
* **Framework**: FastAPI (Python 3.12+)
* **Database**: SQLite (Primary storage) & SQLAlchemy ORM
* **Caching**: Redis (For high-performance read endpoints)
* **Migrations**: Alembic
* **Authentication**: JWT Bearer Tokens
* **Architecture**: Repository Pattern, Schema Validation (Pydantic), Feature-first layout

### Frontend 🅰️
* **Framework**: Angular 17 (Standalone Components, Signals)
* **Mobile Engine**: Ionic & Capacitor 6
* **Admin Portal UI**: Angular Material 3
* **Design System**: Custom Apple Human Interface Guidelines (HIG) theme engine with frosted glass (blur), smooth micro-animations, and dynamic dark mode support.
* **Workspace**: Angular CLI multi-project workspace (`mobile-app` & `admin-portal`)

## Project Structure

```text
d:\10xDaily\
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/v1/endpoints/ # API Routes by feature
│   │   ├── core/             # Security, Config, Cache
│   │   ├── db/               # SQLAlchemy setup
│   │   ├── models/           # DB Schema Definitions
│   │   └── schemas/          # Pydantic validation models
│   ├── scripts/              # Seeding scripts (seed_data.py)
│   └── tests/                # Pytest suites
└── frontend/
    ├── projects/
    │   ├── admin-portal/     # Angular Material CMS dashboard
    │   └── mobile-app/       # Ionic/Capacitor iOS/Android app
    └── shared-styles/        # Global SCSS theme engine
```

## Getting Started

### 1. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run migrations to create SQLite database
alembic upgrade head

# Seed initial topic data
python -m scripts.seed_data

# Start the FastAPI server (Runs on http://localhost:8000)
uvicorn app.main:app --reload
```
*Note: Make sure Redis is running locally on port 6379 for caching.*

### 2. Frontend Setup

```bash
cd frontend
npm install

# Start the Mobile App (Ionic interface)
npm run start:mobile

# Start the Admin Portal (Material interface)
npm run start:admin
```

## Features Implemented

* **Vocabulary**: 3D animated flip cards with pronunciation.
* **AI News**: Inshorts-style infinite scrolling cards with AI summaries.
* **Coding**: LeetCode-style problem viewer with hints and solutions.
* **Finance**: Bite-sized financial advice and calculators.
* **Health**: Daily actionable health advice.
* **Spirituality**: Philosophical stories and reflections.
* **Admin Portal**: CMS dashboard to manage all learning data.
* **Progress Tracking**: Daily streaks and streak rings.

## Testing

Backend testing is implemented using `pytest`.

```bash
cd backend
python -m pytest tests/
```
