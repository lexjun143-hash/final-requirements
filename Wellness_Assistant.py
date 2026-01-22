import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(page_title="Campus Health & Wellness AI Assistant")

# --------------------------------------------------------
# CHECK IF SNOWFLAKE IS CONFIGURED
# --------------------------------------------------------
SNOWFLAKE_ENABLED = "snowflake" in st.secrets

# --------------------------------------------------------
# SNOWFLAKE CONNECTION (SAFE)
# --------------------------------------------------------
@st.cache_resource
def init_connection():
    if not SNOWFLAKE_ENABLED:
        return None
    try:
        return get_active_session()
    except Exception:
        return Session.builder.configs({
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"],
            "role": st.secrets["snowflake"].get("role", "ACCOUNTADMIN")
        }).create()

session = init_connection()

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("🏥 Campus Health & Wellness AI Assistant")

if not SNOWFLAKE_ENABLED:
    st.warning("⚠️ Running in **Demo Mode** (Snowflake not configured)")

# --------------------------------------------------------
# SEMANTIC RETRIEVAL
# --------------------------------------------------------
def retrieve_context(user_input, top_k=3):
    if not SNOWFLAKE_ENABLED:
        return pd.DataFrame({
            "QUESTION": ["What should I do if I feel unwell on campus?"],
            "ANSWER": [
                "Visit the campus clinic, inform your instructor if needed, and rest properly."
            ]
        })

    sql = f"""
        WITH q AS (
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'snowflake-arctic-embed-m',
                '{user_input.replace("'", "''")}'
            ) AS emb
        )
        SELECT
            QUESTION,
            ANSWER,
            VECTOR_COSINE_SIMILARITY(QUESTION_EMBED, q.emb) AS score
        FROM HEALTH_GUIDE_TABLE, q
        ORDER BY score DESC
        LIMIT {top_k}
    """
    return session.sql(sql).to_pandas()

# --------------------------------------------------------
# PROMPT BUILDER (RAG)
# --------------------------------------------------------
def build_prompt(context_df, user_question):
    context_text = "\n\n".join(
        f"Q: {row.QUESTION}\nA: {row.ANSWER}"
        for _, row in context_df.iterrows()
    )

    return f"""
You are an AI assistant for a university campus health and wellness office.

Use the reference health guidelines below to answer the question.
If no guideline directly applies, clearly state that and provide general wellness best practices.
Do NOT provide medical diagnoses or invent policies.

### Reference Guidelines
{context_text}

### User Question
{user_question}
"""

# --------------------------------------------------------
# CHAT STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("Ask a health or wellness question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing guidelines..."):
            try:
                context_df = retrieve_context(prompt)
                ai_prompt = build_prompt(context_df, prompt)

                if SNOWFLAKE_ENABLED:
                    query = f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'mistral-large2',
                            '{ai_prompt.replace("'", "''")}'
                        ) AS RESPONSE
                    """
                    result = session.sql(query).collect()
                    response = result[0]["RESPONSE"]
                else:
                    response = (
                        "Based on campus wellness guidelines, it is recommended to "
                        "seek assistance from the campus clinic, maintain proper rest, "
                        "and follow healthy lifestyle practices."
                    )

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                st.error(f"❌ AI Error: {e}")

# --------------------------------------------------------
# RESTART BUTTON
# --------------------------------------------------------
if st.button("🔄 Restart Chat"):
    st.session_state.messages = []
    st.success("Chat cleared.")
