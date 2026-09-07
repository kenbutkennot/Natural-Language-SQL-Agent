from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from .config import Settings
from .database import create_database


SYSTEM_PROMPT = """
You are a careful SQL analyst. Answer the user's question using the connected database.
Inspect the schema before querying. Generate read-only SQL only: never INSERT, UPDATE,
DELETE, DROP, ALTER, or otherwise modify data. Limit large result sets, explain the
answer briefly, and include relevant values from the query result.
""".strip()


def _model_options(model: str) -> dict[str, object]:
    options: dict[str, object] = {}
    if "fixed" not in model.lower() and "lite" not in model.lower():
        options["temperature"] = 0
    return options


def build_agent(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        **_model_options(settings.gemini_model),
    )
    database = create_database(settings.database_url)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    return create_sql_agent(
        llm=llm,
        db=database,
        agent_type="tool-calling",
        prompt=prompt,
        verbose=False,
    )
