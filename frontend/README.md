# Boloka Frontend

React (Vite) + Tailwind CSS + Themeloom. Built as a Progressive Web App and wrapped into a signed Android APK with Capacitor for release.

This folder is a placeholder until the app is scaffolded (issue #2).

## Run (once scaffolded)

    npm ci
    npm run dev

## Environment

Copy .env.example to .env and set:

- VITE_SUPABASE_URL
- VITE_SUPABASE_ANON_KEY
- VITE_API_BASE_URL

Never commit .env. The anon key is the only Supabase key used on the client and is protected by Row-Level Security.

See ../agents.md for conventions, ../docs/design.md for screens and design direction, and ../docs/api.md for the API contract.
