

import pytest


def test_build_agent_requires_google_api_key():
    from sql_agent.agent import build_agent
    from sql_agent.config import Settings

    settings = Settings(database_url="sqlite:///:memory:", google_api_key=None)

    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY is not set"):
        build_agent(settings)


def test_build_agent_uses_settings(monkeypatch):
    from sql_agent.agent import build_agent
    from sql_agent.config import Settings

    captured = {}

    class FakeLLM:
        def __init__(self, **kwargs):
            captured["llm_kwargs"] = kwargs

    def fake_create_sql_agent(*, llm, db, agent_type, prompt, verbose):
        captured["llm"] = llm
        captured["db"] = db
        captured["agent_type"] = agent_type
        captured["prompt"] = prompt
        captured["verbose"] = verbose
        return {"status": "ok"}

    monkeypatch.setattr("sql_agent.agent.ChatGoogleGenerativeAI", FakeLLM)
    monkeypatch.setattr("sql_agent.agent.create_sql_agent", fake_create_sql_agent)

    settings = Settings(
        database_url="sqlite:///:memory:",
        google_api_key="test-key",
        gemini_model="gemini-2.5-flash",
    )

    agent = build_agent(settings)

    assert agent == {"status": "ok"}
    assert captured["llm_kwargs"]["model"] == "gemini-2.5-flash"
    assert captured["llm_kwargs"]["google_api_key"] == "test-key"
    assert captured["agent_type"] == "tool-calling"
    assert captured["verbose"] is False
    assert "read-only SQL" in captured["prompt"].messages[0].prompt.template.lower()


def test_cli_seed_demo_database_option(monkeypatch, capsys):
    import sql_agent.cli as cli

    captured = {}

    monkeypatch.setattr(cli, "Settings", type("S", (), {"from_env": staticmethod(lambda: cli.Settings("sqlite:///:memory:"))}))
    monkeypatch.setattr(cli, "seed_demo_database", lambda database_url: captured.setdefault("database_url", database_url))
    monkeypatch.setattr("sys.argv", ["sql-agent", "--seed-demo"])

    cli.main()

    assert captured["database_url"] == "sqlite:///:memory:"
    assert "Demo database ready" in capsys.readouterr().out


def test_cli_question_path_invokes_agent(monkeypatch, capsys):
    import sql_agent.cli as cli

    class FakeAgent:
        def __init__(self):
            self.calls = []

        def invoke(self, payload):
            self.calls.append(payload)
            return {"output": "Top customer is Ada."}

    fake_agent = FakeAgent()
    monkeypatch.setattr(cli, "Settings", type("S", (), {"from_env": staticmethod(lambda: cli.Settings("sqlite:///:memory:", google_api_key="test-key"))}))
    monkeypatch.setattr(cli, "build_agent", lambda settings: fake_agent)
    monkeypatch.setattr("sys.argv", ["sql-agent", "Which customer spent the most?"])

    cli.main()

    assert fake_agent.calls == [{"input": "Which customer spent the most?"}]
    assert "Top customer is Ada." in capsys.readouterr().out
