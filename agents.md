# AGENTS.md

Guidance for humans and AI coding agents working in the Boloka repository. Read this before making changes.

## What Boloka is
A money app for people with irregular incomes. It records earnings and upcoming costs, shows an inspectable pandas-based planning estimate, and explains conditional set-aside amounts. Do not claim calibrated accuracy, confidence, likely risk or a precise shortfall date without supporting evidence. Built for the Financial Inclusion track of FNB App of the Year 2026.

## Tech stack
- Frontend: React (Vite), Tailwind CSS, Themeloom, PWA. Charts with Recharts.
- Mobile: Capacitor (signed Android APK).
- Backend: Python, FastAPI.
- Intelligence: pandas-based cash-planning baseline. No AI/ML dependency without a validated product reason.
- Data and auth: Supabase (PostgreSQL and Auth, with Row-Level Security).
- Hosting: Vercel (frontend), Render (backend).

## Repository structure (target)
- /frontend: the React app.
- /backend: the FastAPI app.
- /.github/workflows: CI (ci.yml) and CD (deploy.yml).
- planning.md, status.md, agents.md: project docs.

## Getting started
Frontend:

    cd frontend
    npm ci
    npm run dev

Backend:

    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Environment: copy .env.example to .env and fill in the values. Never commit .env.

## Conventions
- Branches: feat/..., fix/..., chore/.... No direct commits to main.
- Pull requests: reference the issue (Closes #NN), keep them small, and ensure CI passes.
- Commit messages: imperative mood, for example Add forecast endpoint.
- Python: ruff for linting, type hints throughout, Pydantic models for request and response bodies.
- JavaScript: ESLint, small functional React components.

## Security rules (see the SSDL)
- No secrets in the repository or the client bundle. Secrets live only in environment variables.
- The Supabase anon key is used on the client and is protected by Row-Level Security. The service-role key is server-side only.
- Validate all inputs with Pydantic. Use parameterised queries only.
- Every protected endpoint authenticates the user and never trusts a client-supplied identifier for ownership.
- Enforce row ownership at the database layer (RLS), not only in application code.

## CI/CD
- Every push and pull request to main runs ci.yml (lint, build, and test for frontend and backend).
- Merges to main run deploy.yml (Vercel and Render) once the deploy secrets are set.
- Keep main green at all times.

## For AI agents
- Follow this file and planning.md. Work one issue at a time and reference it in the pull request.
- Do not add secrets, do not weaken the security rules above, and do not commit build artifacts.
- Prefer small, reviewed pull requests over large direct changes to main.
