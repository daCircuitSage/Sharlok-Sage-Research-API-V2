# Sharlok Sage V2 Deep Researcher

This repository contains a Django REST API backend for generating research reports and a React frontend for interacting with the API. The backend logic, research flow, models, and API design are maintained by the project owner. The frontend UI was added separately and is the only part that was created with AI assistance.

## Overview

The project lets a user:

- sign in with Google
- submit a research topic
- fetch a generated report from the backend
- view recent results in the web UI

The backend uses a LangChain-based flow to gather sources, process them, and return a report with confidence details.

## Features

- Google authentication flow for the frontend
- JWT-based authentication using Django REST Framework SimpleJWT
- Research topic submission endpoint
- Report generation using the backend pipeline
- SQLite-based result storage
- React frontend for login, topic submission, and report viewing

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- Django CORS headers
- JWT authentication
- LangChain / LangGraph
- Mistral AI
- Tavily API
- BeautifulSoup / Playwright
- SQLite

### Frontend
- React
- Vite
- Axios
- Google OAuth React package

## Project Structure

- `config/` — Django project settings and URL configuration
- `research/` — API views, serializers, models, auth logic, and service layer
- `agents.py` — research orchestration logic
- `pipeline.py` / `pipleline.py` — pipeline entry point scripts
- `tools.py` — scraping, validation, search, and report-building helpers
- `frontend/` — React frontend application
- `Requirements.txt` — Python backend dependencies
- `example.env` — environment variable template
- `db.sqlite3` — local SQLite database

## Environment Variables

Create a `.env` file in the project root using the values from `example.env`.

Example:

```env
TAVILY_API_KEY=your_tavily_key
MISTRAL_API_KEY=your_mistral_key
```

For the frontend, create a `.env` file inside the `frontend/` folder:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

## Installation

### Backend

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r Requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

### Frontend

1. Move into the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

## Running the Project

### Start the backend

```bash
python manage.py runserver
```

The API will run at:

```text
http://127.0.0.1:8000
```

### Start the frontend

```bash
cd frontend
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

## API Endpoints

### Google auth

```http
POST /auth/google/
```

Request body:

```json
{
  "id_token": "google_id_token"
}
```

Response:

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Refresh token

```http
POST /auth/token/refresh/
```

Request body:

```json
{
  "refresh": "refresh_token"
}
```

### Research generation

```http
POST /research/
```

Request body:

```json
{
  "topic": "Artificial intelligence trends in 2026"
}
```

Response:

```json
{
  "topic": "Artificial intelligence trends in 2026",
  "report": "Generated report text",
  "confidence": 0.82
}
```

## Frontend Notes

- The frontend is a React + Vite app.
- It handles Google login, token storage, and sending requests to the backend.
- The frontend is the only part that was created with AI assistance.

## Notes

- The default database is SQLite, so it is easy to run locally.
- The backend expects a JSON payload with a single `topic` field for research requests.
- If you use a different frontend port during development, make sure the same origin is allowed in both Django CORS settings and the Google OAuth console.

## License

No license file is currently included in the repository.

