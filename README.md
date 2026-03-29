# Backend Exercise — Media Processing Pipeline

## Context

You've just joined the team. There's a service that accepts media file and provide transcription.
We though about using Whisper through Hugging Face API.

Your job: **make it work**

---

## What's in the repo

```
app/
├── main.py       ← FastAPI app
├── worker.py     ← Celery worker
├── models.py     ← MongoEngine models
├── config.py     ← Settings (reads from .env)
└── tests/
    ├── conftest.py
    └── test_pipeline.py  

ui/
├── src/
│   ├── App.tsx
│   └── components/
│       ├── Uploader.tsx
│       ├── JobStatus.tsx
│       └── ResultCard.tsx
```

---

## Setup

### 1. HuggingFace token (free)

We want to use HuggingFace for the AI integration task.

1. Create a free account at https://huggingface.co/join
2. Go to https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained
3. Give it a name and click **Create token**, then copy it

```bash
cp .env.example .env
# Edit .env and set HF_TOKEN=hf_your_token_here
```

> **Important:** `.env` is in `.gitignore`. Never commit it.

### 2. Run the stack

```bash
docker-compose up --build
```

## Your Tasks

### Required
1. **Wire up the AI integration** 
2. **Working UI and Server** 
3. **Fill in `SUBMISSION.md`** — explain what you did and why, how you implemented the HF integration, and answer the system design question.

### Bonus — not tested, but noticed

Pick any that feel natural. Don't force it.

- Add a health check that verifies MongoDB and RabbitMQ are reachable (not just `{"status": "ok"}`)
- Add structured logging (job_id, duration, status) using `structlog` or stdlib
- Add a `GET /jobs` endpoint to list recent jobs with pagination and show them on the ui
- Full testing coverage

---

## Submission

1. Push your solution to a **public GitHub repository**
2. Fill in `SUBMISSION.md`
3. Share the repo link

The repo must pass `docker-compose up` without any manual steps beyond setting up `.env`.
