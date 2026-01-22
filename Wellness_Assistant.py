import streamlit as st

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Self-Care & Wellness Chatbot",
    page_icon="💬",
    layout="centered"
)

# --------------------------------------------------------
# INTENT & EMOTION DETECTION
# --------------------------------------------------------
def detect_intent(text):
    text = text.lower()

    if any(word in text for word in ["suicide", "kill myself", "hurt myself", "end my life"]):
        return "emergency"

    if any(word in text for word in ["stress", "anxious", "anxiety", "pressure", "overwhelmed"]):
        return "stress"

    if any(word in text for word in ["sad", "down", "lonely", "cry", "depressed"]):
        return "sad"

    if any(word in text for word in ["tired", "exhausted", "burnout", "fatigue"]):
        return "fatigue"

    if any(word in text for word in ["sleep", "insomnia", "can't sleep"]):
        return "sleep"

    if any(word in text for word in ["help", "what can you do", "features"]):
        return "features"

    return "general"

# --------------------------------------------------------
# FOLLOW-UP QUESTIONS
# --------------------------------------------------------
def follow_up_question(intent):
    follow_ups = {
        "stress": "Do you want to share what’s been causing the stress lately?",
        "sad": "Would you like to talk more about what’s been weighing on you?",
        "fatigue": "Has this tiredness been going on for a while?",
        "sleep": "What usually makes it hardest for you to fall asleep?",
        "general": "Would you like to tell me more about how you’re feeling right now?"
    }
    return follow_ups.get(intent, follow_ups["general"])

# --------------------------------------------------------
# SUPPORTIVE RESPONSES
# --------------------------------------------------------
def handle_intent(intent):
    responses = {
        "features": (
            "I’m here to support you emotionally and mentally. 💙\n\n"
            "I can help you by:\n"
            "• Listening to your thoughts and feelings\n"
            "• Helping you process stress or anxiety\n"
            "• Offering gentle self-care suggestions\n"
            "• Giving you a safe space to talk freely\n\n"
            "You can share as much as you want."
        ),

        "stress": (
            "That sounds really overwhelming. 💛\n\n"
            "It’s okay to feel stressed when things pile up."
        ),

        "sad": (
            "I’m really glad you told me this. 💙\n\n"
            "What you’re feeling matters."
        ),

        "fatigue": (
            "Being constantly tired can drain you emotionally and physically. 😴\n\n"
            "You deserve rest."
        ),

        "sleep": (
            "Sleep problems can be frustrating.\n\n"
            "Your mind might just need some calm right now."
        ),

        "emergency": (
            "I’m really concerned about your safety. ❤️\n\n"
            "You deserve immediate support. Please reach out to someone you trust "
            "or contact local emergency services right now."
        ),

        "general": (
            "I’m here with you. 😊\n\n"
            "You can talk to me anytime."
        )
    }

    return responses.get(intent, responses["general"])

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("💬 Campus Self-Care & Wellness Chatbot")
st.caption(
    "A supportive space where you can talk freely until you feel better."
)

# --------------------------------------------------------
# CHAT STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_reply_done" not in st.session_state:
    st.session_state.first_reply_done = False

# --------------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("Type your thoughts here…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Listening..."):

            # FIRST MESSAGE ONLY
            if not st.session_state.first_reply_done:
                response = "Hello! 👋😊\n\nWhat can I do for you today?"
                st.session_state.first_reply_done = True
            else:
                intent = detect_intent(prompt)
                response = (
                    f"{handle_intent(intent)}\n\n"
                    f"{follow_up_question(intent)}"
                )

            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

# --------------------------------------------------------
# RESET BUTTON (FIXED & FINAL)
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.messages.clear()
    st.session_state.first_reply_done = False
    st.rerun()
