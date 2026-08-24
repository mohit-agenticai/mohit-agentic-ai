# Hugging Face Space (Docker) — Deploy guide

This branch (hf/streamlit-space-init) contains a Docker-based Streamlit app that integrates with Supabase and exposes a UI toggle between two engine modes:

- Mohit Agentic AI — tool orchestration & web search (orchestrator)
- BharatGpilot — deterministic zero-temperature code emitter (engine)

Files included
- app.py — Streamlit application UI and logic (already committed)
- Dockerfile — Docker build for HF Spaces
- requirements.txt — Python dependencies
- .env.example — example environment variables (do NOT commit secrets)
- start.sh — helper entrypoint
- .gitignore

Quick deploy steps (if you want to finish manually)
1. Create a new Hugging Face Space using the Docker template under your account.
2. In the Space settings, add the following repository secrets:
   - SUPABASE_URL
   - SUPABASE_KEY
   - (optional) GROQ_API_KEY, OPENAI_API_KEY
   - ADMIN_EMAIL (optional admin account email)
3. Push the contents of this branch into the Space repo (or upload code via the HF web editor).
4. HF will build the Docker image and run the Streamlit app. The app will be available at the Space URL.

If you invited the automation handle (mohit-agenticai-automation) with Write access to this repo and your Hugging Face account, I will:
- Create the Space under your HF username, push code, set secrets, trigger build, and monitor logs until the Space is live.

Security
- Do not commit real keys. Use Space secrets for SUPABASE_KEY and LLM/API keys.

Support
- If you want, I can also add SQL seed scripts and billing/token accounting scripts. Reply with your preferences.
