# LangChain SQL Agent

A small natural-language SQL agent built with LangChain, SQLAlchemy, and Gemini tool calling. It defaults to a local SQLite database so the project can be tried without configuring a database server.

## Setup

```powershell
.venv\Scripts\python.exe -m pip install -e ".[test]"
Copy-Item .env.example .env
.venv\Scripts\python.exe -m sql_agent.cli --seed-demo
```

Launch the visual Streamlit interface:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[test]"
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Add a `GOOGLE_API_KEY` to `.env`, then start the interactive terminal chat:

```powershell
.venv\Scripts\python.exe -m sql_agent.cli
```

Use `exit`, `quit`, or `:q` to leave. You can still run one question directly:

```powershell
.venv\Scripts\python.exe -m sql_agent.cli "Which customer spent the most?"
```

Set `DATABASE_URL` in `.env` to connect to another SQLAlchemy-supported database. The agent is instructed to generate read-only SQL, but production deployments should still enforce database permissions at the database user level.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest
```
