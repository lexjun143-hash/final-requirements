import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Self-Care & Wellness Chatbot",
    page_icon="💬",
    layout="centered"
)

# --------------------------------------------------------
# GREETING & SMALL TALK LOGIC
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
        "Welcome to the **Campus Self-Care & Wellness Chatbot**.\n\n"
        "I’m here to help you with:\n"
        "• Self-care tips\n"
        "• Stress and mental wellness\n"
        "• Understanding mild symptoms\n"
        "• Healthy daily habits\n\n"
        "How can I help you today?"
    )

# --------------------------------------------------------
# CHECK SNOWFLAKE CONFIGURATION
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
    "A friendly AI chatbot that provides self-care guidance, "
    "wellness tips, and student support — no clinic visit required."
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
                "What should students do for mild health concerns?"
            ],
            "ANSWER": [
                "For mild concerns, students can rest, stay hydrated, "
                "eat balanced meals, manage stress, and monitor symptoms."
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
# PROMPT BUILDER
# --------------------------------------------------------
def build_prompt(context_df, user_question):
    context_text = "\n\n".join(
        f"Q: {row.QUESTION}\nA: {row.ANSWER}"
        for _, row in context_df.iterrows()
    )

    return f"""
You are a calm, polite, and supportive self-care wellness chatbot
for university students.

PURPOSE:
- Provide self-care and wellness guidance
- Offer mental and lifestyle support
- Help users understand mild symptoms

RULES:
- DO NOT diagnose medical conditions
- DO NOT prescribe medication
- DO NOT replace healthcare professionals
- Encourage professional help ONLY if symptoms are severe or persistent

STYLE:
- Customer-service friendly
- Reassuring and non-alarming
- Easy to understand

### Wellness References
{context_text}

### User Message
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
# CHAT INPUT HANDLER
# --------------------------------------------------------
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Responding..."):
            try:
                # GREETING HANDLER (FIRST INTERACTION)
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
                            "Thanks for sharing 😊\n\n"
                            "For mild concerns, simple self-care can help a lot:\n"
                            "• Get enough rest\n"
                            "• Stay hydrated\n"
                            "• Eat nutritious meals\n"
                            "• Manage stress\n\n"
                            "If your symptoms become severe or don’t improve, "
                            "seeking professional help would be a good next step."
                        )

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                st.error(f"❌ Chatbot Error: {e}")

# --------------------------------------------------------
# RESET BUTTON
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.messages = []
    st.success("Conversation cleared.")
