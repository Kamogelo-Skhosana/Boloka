# Boloka Backend

Python + FastAPI. Serves the CRUD and forecasting API over the Supabase Postgres database. The forecasting engine uses pandas with Prophet / scikit-learn.

This folder is a placeholder until the API is scaffolded (issue #3).

## Run (once scaffolded)

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

## Environment

Copy .env.example to .env and set:

- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY   (server-side only, never shipped to the client)
- SUPABASE_JWT_SECRET         (used to verify user access tokens)

Never commit .env.

See ../docs/api.md for the API contract and ../supabase/schema.sql for the database schema.
