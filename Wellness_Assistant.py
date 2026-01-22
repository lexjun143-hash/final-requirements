import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(
    page_title="Campus Self-Care & Wellness Chatbot",
    page_icon="💬"
)

# --------------------------------------------------------
# GREETING DETECTION
# --------------------------------------------------------
def is_greeting(text):
    greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon",
        "good evening", "start", "help"
    ]
    text = text.lower().strip()
    return any(greet in text for greet in greetings)

def greeting_response():
    return (
        "Hello! 👋😊\n\n"
        "I’m your **Campus Self-Care & Wellness Chatbot**. "
        "I can help you with:\n"
        "- Self-care tips\n"
        "- Stress and mental wellness guidance\n"
        "- Understanding mild symptoms\n"
        "- Healthy daily habits\n\n"
        "How can I assist you today?"
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
    "A friendly self-care chatbot that supports students "
    "without requiring clinic or hospital visits."
)

if not SNOWFLAKE_ENABLED:
    st.info("ℹ️ Demo Mode: General wellness guidance")

# --------------------------------------------------------
# CONTEXT RETRIEVAL
# --------------------------------------------------------
def retrieve_context(user_input, top_k=3):
    if not SNOWFLAKE_ENABLED:
        return pd.DataFrame({
            "QUESTION": [
                "How can students take care of themselves when feeling unwell?"
            ],
            "ANSWER": [
                "Self-care includes rest, hydration, balanced meals, stress management, "
                "and monitoring symptoms over time."
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
# PROMPT BUILDER (SELF-CARE)
# --------------------------------------------------------
def build_prompt(context_df, user_question):
    context_text = "\n\n".join(
        f"Q: {row.QUESTION}\nA: {row.ANSWER}"
        for _, row in context_df.iterrows()
    )

    return f"""
You are a polite, friendly, and supportive self-care wellness chatbot
for university students.

Your role:
- Provide self-care guidance
- Offer stress and lifestyle tips
- Help users understand mild symptoms
- Encourage healthy habits

Rules:
- No medical diagnosis
- No prescriptions
- Suggest professional help only if symptoms are severe or persistent

### Wellness References
{context_text}

### User Message
{user_question}

### Response Style
- Customer-service friendly
- Calm and supportive
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
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Responding..."):
            try:
                # 🔹 GREETING HANDLER
                if is_greeting(prompt) and len(st.session_state.messages) <= 2:
                    response = greeting_response()

                else:
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
                            "Thanks for reaching out 😊 "
                            "For mild concerns, simple self-care like rest, hydration, "
                            "proper nutrition, and stress management can help. "
                            "Let me know what you’re experiencing."
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
