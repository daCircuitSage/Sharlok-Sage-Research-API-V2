# Sharlok Sage V2 Deep Researcher

A Django REST API project that generates research reports from a user topic using a LangChain-based pipeline. The system collects web sources, scrapes relevant pages, synthesizes findings, verifies confidence, and returns a structured report.

## Features

- Accepts a topic and generates a research report
- Uses Tavily search results and web scraping for source collection
- Builds a final report with key findings, contradictions, and sources
- Stores completed research results in a SQLite database
- Exposes a simple REST endpoint for API access

## Tech Stack

- Python
- Django
- Django REST Framework
- LangChain / LangGraph
- Mistral AI
- Tavily API
- BeautifulSoup / Playwright
- SQLite (default setup)

## Project Structure

- `config/` — Django settings and URL routing
- `research/` — API views, serializers, models, and service layer
- `agents.py` — research orchestration logic
- `pipeline.py` / `pipleline.py` — CLI pipeline entry points
- `tools.py` — search, scraping, deduplication, verification, and report generation helpers
- `Requirements.txt` — Python dependencies
- `example.env` — environment variable template

## Prerequisites

- Python 3.10+
- A virtual environment is recommended
- API keys for:
  - Tavily
  - Mistral AI

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:

```bash
pip install -r Requirements.txt
```

4. Copy the example environment file and fill in your API keys:

```bash
copy example.env .env
```

Then update `.env` with your credentials:

```env
TAVILY_API_KEY=your_tavily_key
MISTRAL_API_KEY=your_mistral_key
```

## Running the Server

Apply database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/research/
```

## API Usage

### Request

Send a `POST` request with a topic:

```bash
curl -X POST http://127.0.0.1:8000/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial intelligence trends in 2026"}'
```

### Response Example

```json
{
  "topic": "Artificial intelligence trends in 2026",
  "report": "...generated report...",
  "confidence": 0.82
}
```

## Running the Pipeline Script

You can also run the research pipeline manually from the CLI:

```bash
python pipeline.py
```

The script will prompt you for a topic and then print the generated report.

## Notes

- The project uses SQLite by default, so it is suitable for local development.
- Some files contain small naming inconsistencies (for example, `pipleline.py` vs. `pipeline.py`). If you see import issues, confirm which script you are running.
- The API currently expects a JSON payload with a single `topic` field.

## License

This project does not currently include a license file. If you plan to share or distribute it publicly, consider adding one.
