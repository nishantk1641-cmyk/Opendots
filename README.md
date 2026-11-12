# OpenDots

Self-hostable starter workspace for AI coworkers (Dots).

## Included
- React + TypeScript workspace UI: Spaces, Dots, chat, searchable page library, nested pages, draft review, activity/computer panel.
- FastAPI backend with health, spaces, agents, pages, chat and draft-review endpoints.
- PostgreSQL + Redis via Docker Compose.
- Explicit setup states for optional AI, Slack, LiveKit and browser services.

## Quick start
1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD` and `APP_SECRET`.
2. Run `docker compose up --build`.
3. Open http://localhost:3000 and API docs at http://localhost:8000/docs.

The UI ships with demo workspace data so it can be explored without integrations. The computer panel is currently a live-activity placeholder, not a connected remote desktop. Voice and Slack show setup states until credentials and their adapters are configured. Do not expose this starter publicly before adding authentication, tenant isolation, rate limits, secret management and production-grade sandboxing.

## Integrations
- AI: set `OPENAI_API_KEY` or `OLLAMA_BASE_URL`; implement/choose a provider adapter in `backend/main.py`.
- Slack: create a Slack app, configure OAuth and Events API; use Socket Mode for local development or an HTTPS Events endpoint in production. See https://docs.slack.dev/apis/events-api/ and https://docs.slack.dev/apis/events-api/using-socket-mode/
- Voice: configure a LiveKit project and add a token-issuing endpoint; never expose API secrets in the browser.
- Browser: run Playwright in a separate, network-restricted worker container. Require approval for writes, downloads and external submissions.
