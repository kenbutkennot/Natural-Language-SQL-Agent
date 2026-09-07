import streamlit as st

from sql_agent.agent import build_agent
from sql_agent.config import Settings
from sql_agent.database import seed_demo_database

BLACK = "\033[30m"
WHITE = "\033[97m"
GRAY = "\033[90m"

st.set_page_config(
    page_title="SQL Agent",
    page_icon="▣",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] { background: #050b0f; }
    [data-testid="stSidebar"] { background: #08151b; border-right: 1px solid #00f5ff; }
    [data-testid="stChatMessage"] { background: #0b1b21; }
    body, p, span, label, div, h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    [data-testid="stChatMessageContent"] { color: #e8fbff; }
    .hero { padding: 1.5rem 0 1rem; }
    .eyebrow { color: #00f5ff; font-size: .78rem; font-weight: 700;
               letter-spacing: .12em; text-transform: uppercase; }
    .hero h1 { color: #00f5ff; text-shadow: 0 0 14px rgba(0, 245, 255, .5); }
    .hero p { color: #e8fbff; }
    input, textarea,
    [data-baseweb="select"], [data-baseweb="input"] {
        background: #0b1b21 !important;
        color: #e8fbff !important;
        border-color: #00f5ff !important;
    }
    button {
        background: #10252b !important;
        color: #ffe600 !important;
        border: 1px solid #ffe600 !important;
        box-shadow: 0 0 8px rgba(255, 230, 0, .25);
    }
    button:hover { background: #ffe600 !important; color: #050b0f !important; }
    [data-testid="stChatMessage"] { border: 1px solid #00f5ff; border-radius: 12px; box-shadow: 0 0 10px rgba(0, 245, 255, .12); }
    [data-testid="stChatInput"] { border-color: #00f5ff !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #9deff5; opacity: 1; }
    [data-testid="stCaptionContainer"] { color: #ffe600 !important; }
    [data-testid="stStatusWidget"] { color: #ffe600 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = Settings.from_env()

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">LangChain + Gemini</div>
      <h1>SQL Agent</h1>
      <p>Ask questions about your database in plain language.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Connection")
    st.caption(f"Model: `{settings.gemini_model}`")
    st.caption(f"Database: `{settings.database_url}`")

    if st.button("Seed demo database", use_container_width=True):
        try:
            seed_demo_database(settings.database_url)
            st.success("Demo database is ready.")
            st.session_state.pop("agent", None)
        except Exception as error:
            st.error(str(error))

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("The agent uses read-only SQL instructions. Enforce read-only permissions at the database level for production.")


@st.cache_resource(show_spinner=False)
def get_agent(database_url: str, model: str, api_key: str):
    return build_agent(
        Settings(
            database_url=database_url,
            gemini_model=model,
            google_api_key=api_key,
        )
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Try: Which customer spent the most?"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not settings.google_api_key:
            st.error("GOOGLE_API_KEY is not configured. Add it to your .env file.")
        else:
            try:
                agent = get_agent(
                    settings.database_url,
                    settings.gemini_model,
                    settings.google_api_key,
                )
                with st.spinner("Analyzing your question..."):
                    result = agent.invoke({"input": question})
                answer = result.get("output", "No answer returned.")
                if isinstance(answer, list):
                    answer = "\n".join(
                        item.get("text", "") if isinstance(item, dict) else str(item)
                        for item in answer
                    ).strip()
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as error:
                st.error(f"The agent could not complete that request: {error}")
