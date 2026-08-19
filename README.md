# 10xDaily 🚀

> "Become 1% Smarter Every Day."

10xDaily is a full-stack, production-grade learning operating system designed to deliver high-quality, bite-sized lessons across various domains including Vocabulary, Tech/AI News, Coding, Finance, Health, Spirituality, and Interactive Games.

## Architecture & Tech Stack

This project strictly adheres to Clean Architecture principles.

### Backend 🐍
* **Framework**: FastAPI (Python 3.12+)
* **Database**: PostgreSQL (via Supabase) / SQLite (Local) & SQLAlchemy ORM
* **Caching**: In-memory / Redis (For high-performance read endpoints)
* **Migrations**: Alembic
* **Authentication**: JWT Bearer Tokens & Google OAuth
* **Architecture**: Repository Pattern, Schema Validation (Pydantic), Feature-first layout
* **AI Integration**: Groq API for AI summaries and content generation.
* **Email Service**: Resend API & SMTP for user feedback and notifications.

### Frontend 🅰️
* **Framework**: Angular 17 (Standalone Components, Signals)
* **Mobile Engine**: Ionic & Capacitor 6 (Cross-platform iOS/Android support)
* **Admin Portal UI**: Angular Material 3
* **Design System**: Custom Apple Human Interface Guidelines (HIG) theme engine with frosted glass (blur), smooth micro-animations, and dynamic time-based dark mode backgrounds.
* **Workspace**: Angular CLI multi-project workspace (`mobile-app` & `admin-portal`)

## Key Features & Implementations

Over the course of development, we have integrated a rich set of features:

* **Vocabulary Engine**: 3D animated flip cards with pronunciation, and Proficiency Level Categorization (Beginner, Intermediate, Advanced) dynamically powered by Datamuse API.
* **AI News Feed**: Inshorts-style infinite scrolling cards with AI-generated summaries and image compression for fast loading.
* **Games Hub**: A dedicated interactive zone featuring complex logic games:
  * **KenKen**: Math & logic grid puzzle.
  * **Flow**: Connect matching dots without crossing paths.
  * **Connections**: Group related words by categories.
* **Dynamic Aesthetics**: The app dynamically changes backgrounds and color palettes based on the time of day (Morning, Afternoon, Evening, Night).
* **Progress Tracking**: Daily streak tracking with animated circular progress rings.
* **Profile Management**: Profile picture uploads with client-side image compression.
* **Feedback System**: Integrated feedback forms with strict email validation, securely routed via SMTP.
* **Spiritual & Historical**: Daily mythological character profiles and historically accurate event tracking.

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
│   ├── scripts/              # Seeding scripts
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
# Activate the virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

# IMPORTANT: Environment Variables
# Copy the .env.example file to a new file named .env and fill in your keys.
cp .env.example .env

# Start the FastAPI server (Runs on http://localhost:8000)
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install

# Start the Mobile App (Ionic interface)
npm run start:mobile
```

### 3. Publishing to Android (Capacitor)

The mobile frontend is built using Capacitor. To turn it into an Android App:

```bash
cd frontend
# Ensure Android SDK and dependencies are installed
npm install @capacitor/android
npx cap add android
npm run build
npx cap sync android
npx cap open android # Opens Android Studio to build your .aab or .apk
```

## Testing

Backend testing is implemented using `pytest`.

```bash
cd backend
python -m pytest tests/
```
