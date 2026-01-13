# Installation

Get QWED up and running in under 5 minutes.

## Prerequisites

- **Python 3.10+**
- **Docker** (for PostgreSQL)
- **Git**

## Step 1: Clone the Repository

```bash
git clone https://github.com/QWED-AI/qwed-verification.git
cd qwed-verification
```

## Step 2: Install Dependencies

```bash
pip install -e .
```

This installs QWED in editable mode with all dependencies.

## Step 3: Start PostgreSQL

QWED uses PostgreSQL for production workloads. Start it with Docker:

```bash
docker-compose up -d
```

This starts a PostgreSQL instance with:
- **Host:** `localhost:5432`
- **User:** `qwed`
- **Password:** `qwed_secret`
- **Database:** `qwed_db`

## Step 4: Configure Environment

Copy the example environment file and configure your LLM provider:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini title=".env"
# Database
DATABASE_URL=postgresql://qwed:qwed_secret@localhost:5432/qwed_db

# LLM Provider (Choose one)
ACTIVE_PROVIDER=anthropic

# Anthropic / Claude
ANTHROPIC_ENDPOINT=https://your-endpoint.azure.com/anthropic/
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_DEPLOYMENT=claude-sonnet-4-5

# OR Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4-turbo
```

## Step 5: Start the API

```bash
uvicorn qwed_new.api.main:app --reload
```

The API is now running at: **http://localhost:8000**

- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## What's Next?

Head to the [Quick Start](quickstart.md) guide to run your first verification!

