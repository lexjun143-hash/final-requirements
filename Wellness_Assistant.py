import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(
    page_title="Campus Self-Care & Wellness Chatbot",
    page_icon="💬"
)

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
st.title("💬 Campus Self-Care & Wellness Chatbot")
st.caption(
    "A supportive AI chatbot that provides self-care guidance, "
    "wellness tips, and symptom awareness — no clinic visit required."
)

if not SNOWFLAKE_ENABLED:
    st.info("ℹ️ Demo Mode: Using general wellness knowledge")

# --------------------------------------------------------
# CONTEXT RETRIEVAL
# --------------------------------------------------------
def retrieve_context(user_input, top_k=3):
    if not SNOWFLAKE_ENABLED:
        return pd.DataFrame({
            "QUESTION": [
                "What can I do if I feel tired, stressed, or slightly unwell?"
            ],
            "ANSWER": [
                "Rest, hydrate, eat balanced meals, manage stress, and monitor symptoms. "
                "Most mild concerns improve with proper self-care."
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
# PROMPT BUILDER (SELF-CARE FOCUSED)
# --------------------------------------------------------
def build_prompt(context_df, user_question):
    context_text = "\n\n".join(
        f"Q: {row.QUESTION}\nA: {row.ANSWER}"
        for _, row in context_df.iterrows()
    )

    return f"""
You are a friendly, calm, and supportive self-care wellness chatbot
designed for university students.

Your role is to:
- Provide self-care advice
- Suggest lifestyle and mental wellness practices
- Help users understand mild symptoms
- Encourage monitoring and prevention

IMPORTANT RULES:
- DO NOT provide medical diagnoses
- DO NOT prescribe medication
- DO NOT replace doctors
- Only suggest professional help if symptoms are severe, persistent, or worsening

Always:
- Use student-friendly language
- Be reassuring and non-alarming
- Promote healthy daily habits

### Wellness Reference
{context_text}

### User Message
{user_question}

### Response Style
- Supportive
- Practical
- Calm
- Easy to understand
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
if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
                        "Thanks for sharing how you’re feeling. For mild concerns, "
                        "simple self-care like rest, hydration, proper nutrition, "
                        "and stress management can help a lot. "
                        "Try observing your symptoms over time and prioritize sleep. "
                        "If something feels severe or doesn’t improve, seeking "
                        "professional help would be a good next step."
                    )

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                st.error(f"❌ Chatbot Error: {e}")

# --------------------------------------------------------
# RESTART BUTTON
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.messages = []
    st.success("Conversation cleared.")
