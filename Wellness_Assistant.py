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
# INTENT DETECTION
# --------------------------------------------------------
def detect_intent(text):
    text = text.lower()

    if any(word in text for word in ["stress", "anxious", "anxiety", "overwhelmed"]):
        return "stress"

    if any(word in text for word in ["tired", "fatigue", "exhausted", "sleepy"]):
        return "fatigue"

    if any(word in text for word in ["headache", "head hurts"]):
        return "headache"

    if any(word in text for word in ["can't sleep", "insomnia", "sleep"]):
        return "sleep"

    if any(word in text for word in ["what can you do", "help", "features"]):
        return "features"

    return "general"

# --------------------------------------------------------
# CHATBOT RESPONSES (NO AI, SAFE FALLBACK)
# --------------------------------------------------------
def handle_intent(intent):
    responses = {
        "features": (
            "I can help you with:\n\n"
            "• Managing stress and anxiety\n"
            "• Improving sleep habits\n"
            "• Dealing with tiredness or burnout\n"
            "• Understanding mild discomfort like headaches\n"
            "• Daily self-care and wellness tips\n\n"
            "Just tell me what you’re experiencing."
        ),

        "stress": (
            "Feeling stressed is very common, especially with school responsibilities.\n\n"
            "Here are some things you can try:\n"
            "• Take slow, deep breaths for a few minutes\n"
            "• Step away from screens briefly\n"
            "• Break tasks into smaller steps\n"
            "• Talk to someone you trust\n\n"
            "If stress feels constant or overwhelming, it may help to seek professional support."
        ),

        "fatigue": (
            "Feeling tired can come from lack of rest, stress, or busy schedules.\n\n"
            "You may try:\n"
            "• Getting enough sleep\n"
            "• Drinking water regularly\n"
            "• Eating balanced meals\n"
            "• Taking short breaks during the day\n\n"
            "Let me know if this has been going on for a long time."
        ),

        "headache": (
            "Mild headaches can happen due to stress, dehydration, or screen time.\n\n"
            "Helpful self-care tips:\n"
            "• Drink water\n"
            "• Rest your eyes\n"
            "• Stretch your neck and shoulders\n"
            "• Take a short rest in a quiet place\n\n"
            "If headaches become severe or frequent, professional advice may be needed."
        ),

        "sleep": (
            "Sleep problems are common among students.\n\n"
            "You can try:\n"
            "• Going to bed at the same time daily\n"
            "• Avoiding screens before sleep\n"
            "• Creating a calm bedtime routine\n"
            "• Limiting caffeine late in the day\n\n"
            "If sleep issues continue, seeking help could be beneficial."
        ),

        "general": (
            "Thanks for sharing. 😊\n\n"
            "I can help with self-care, stress management, sleep habits, "
            "and understanding mild concerns. "
            "Tell me more about what you’re feeling."
        )
    }

    return responses.get(intent, responses["general"])

# --------------------------------------------------------
# SNOWFLAKE CHECK (OPTIONAL)
# --------------------------------------------------------
SNOWFLAKE_ENABLED = "snowflake" in st.secrets

@st.cache_resource
def init_connection():
    if not SNOWFLAKE_ENABLED:
        return None
    try:
        return get_active_session()
    except Exception:
        return Session.builder.configs(st.secrets["snowflake"]).create()

session = init_connection()

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("💬 Campus Self-Care & Wellness Chatbot")
st.caption("A supportive chatbot for student self-care and daily wellness.")

# --------------------------------------------------------
# CHAT STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_reply_done" not in st.session_state:
    st.session_state.first_reply_done = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Responding..."):

            # 🔹 FIRST CHAT ONLY
            if not st.session_state.first_reply_done:
                response = (
                    "Hello! 👋😊\n\n"
                    "I’m here to help. What can I do for you today?"
                )
                st.session_state.first_reply_done = True

            else:
                intent = detect_intent(prompt)
                response = handle_intent(intent)

            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

# --------------------------------------------------------
# RESET
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.messages = []
    st.session_state.first_reply_done = False
    st.success("Conversation restarted.")
