import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd

# --------------------------------------------------------
# SNOWFLAKE CONNECTION
# --------------------------------------------------------
@st.cache_resource
def init_connection():
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

st.title("🏥 Campus Health & Wellness AI Assistant")

# --------------------------------------------------------
# SEMANTIC RETRIEVAL (CORTEX EMBEDDINGS)
# --------------------------------------------------------
def retrieve_context(user_input, top_k=3):
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

### Answer Requirements
- Clear and supportive
- Student-friendly language
- Actionable advice when appropriate
- No medical hallucinations
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
# CHAT INPUT → AI RESPONSE
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

                query = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'mistral-large2',
                        '{ai_prompt.replace("'", "''")}'
                    ) AS RESPONSE
                """
                result = session.sql(query).collect()
                response = result[0]["RESPONSE"]

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                error_msg = f"❌ AI Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

# --------------------------------------------------------
# RESTART BUTTON
# --------------------------------------------------------
if st.button("🔄 Restart Chat"):
    st.session_state.messages = []
    st.success("Chat cleared.")
