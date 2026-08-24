# Mohit Agentic AI — Hugging Face Streamlit Space (Docker)

This repository contains a Streamlit-based Hugging Face Space (Docker) scaffold that integrates with Supabase for authentication and database access. It provides a UI toggle to switch between two system modes:

- Main System Identity: Mohit Agentic AI — handles tool orchestration and web search.
- Engineering/Coding Engine: bharatGpilot — handles zero-temperature precise code emission.

The hf/streamlit-space-init branch will contain the full Streamlit app, Dockerfile, and deployment instructions. Secrets required (set these in your Hugging Face Space settings as "Repository secrets"):

- SUPABASE_URL
- SUPABASE_KEY

Usage:
1. Create a new Hugging Face Space using the Docker template.
2. Push the contents of the `hf/streamlit-space-init` branch to the Space repository.
3. Set the required repository secrets above.
4. Deploy — the Streamlit app will run and expose a toggle to switch system modes and connect to your Supabase project.

