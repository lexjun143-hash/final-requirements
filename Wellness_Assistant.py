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

    if any(w in text for w in ["suicide", "kill myself", "hurt myself", "end my life"]):
        return "emergency"
    if any(w in text for w in ["stress", "pressure", "overwhelmed", "anxious", "anxiety"]):
        return "stress"
    if any(w in text for w in ["sad", "lonely", "cry", "down", "empty"]):
        return "sad"
    if any(w in text for w in ["tired", "burnout", "exhausted", "fatigue"]):
        return "fatigue"
    if any(w in text for w in ["sleep", "insomnia", "can't sleep"]):
        return "sleep"
    if any(w in text for w in ["help", "features", "what can you do"]):
        return "features"
    return "general"

# --------------------------------------------------------
# CORE SUPPORT RESPONSES
# --------------------------------------------------------
def base_response(intent):
    responses = {
        "stress": "That sounds really overwhelming. 💛 It’s okay to feel this way.",
        "sad": "I’m really glad you shared that with me. 💙 Your feelings matter.",
        "fatigue": "Being that tired can be draining in every way. 😴",
        "sleep": "Sleep struggles can affect everything else. I hear you.",
        "features": (
            "I’m here to listen, support, and gently guide you.\n\n"
            "You can talk about stress, emotions, exhaustion, or anything weighing on you."
        ),
        "emergency": (
            "I’m really concerned about your safety. ❤️\n\n"
            "You deserve immediate support. Please reach out to someone you trust "
            "or local emergency services right now."
        ),
        "general": "I’m here with you. You can share at your own pace."
    }
    return responses.get(intent, responses["general"])

# --------------------------------------------------------
# PROGRESSIVE ADVICE ENGINE
# --------------------------------------------------------
def progressive_advice(intent, depth):
    advice = {
        "stress": [
            "Sometimes taking a short pause and slow breathing can help calm your body.",
            "You might try breaking tasks into smaller, manageable steps.",
            "It can help to ask: *What is one thing I can control right now?*"
        ],
        "sad": [
            "It’s okay to sit with the feeling without judging it.",
            "Doing something small and comforting—like music or a warm drink—can help.",
            "You’ve been carrying a lot. Be gentle with yourself."
        ],
        "fatigue": [
            "Your body might be asking for rest, not productivity.",
            "Even a short mental break can make a difference.",
            "You don’t have to do everything today."
        ],
        "sleep": [
            "Lowering screen time before bed can help your mind slow down.",
            "A calm routine before sleep may signal your body to rest.",
            "It’s okay if sleep doesn’t come immediately—resting still counts."
        ],
        "general": [
            "Taking a moment to breathe slowly can ground you.",
            "Writing down thoughts sometimes helps clear mental space.",
            "You’re allowed to take things one step at a time."
        ]
    }

    tips = advice.get(intent, advice["general"])
    return tips[min(depth, len(tips) - 1)]

# --------------------------------------------------------
# FOLLOW-UP PROMPTS
# --------------------------------------------------------
def follow_up(intent):
    followups = {
        "stress": "Does this situation feel constant, or does it come and go?",
        "sad": "Would you like to tell me what made today especially heavy?",
        "fatigue": "Have you been getting enough rest lately?",
        "sleep": "What usually runs through your mind at night?",
        "general": "Would you like to talk more about what you’re feeling?"
    }
    return followups.get(intent, followups["general"])

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("💬 Campus Self-Care & Wellness Chatbot")
st.caption("A calm space to talk, reflect, and feel supported.")

# --------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_reply_done" not in st.session_state:
    st.session_state.first_reply_done = False

if "depth" not in st.session_state:
    st.session_state.depth = 0

# --------------------------------------------------------
# DISPLAY CHAT
# --------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("You can talk freely here…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Listening..."):

            # FIRST GREETING ONLY
            if not st.session_state.first_reply_done:
                response = "Hello! 👋😊\n\nWhat can I do for you today?"
                st.session_state.first_reply_done = True
                st.session_state.depth = 0
            else:
                intent = detect_intent(prompt)
                base = base_response(intent)
                advice = progressive_advice(intent, st.session_state.depth)
                follow = follow_up(intent)

                response = (
                    f"{base}\n\n"
                    f"💡 *You might consider this:* {advice}\n\n"
                    f"{follow}\n\n"
                    "Let me know if this is helping or if you’d like another approach."
                )

                st.session_state.depth += 1

            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

# --------------------------------------------------------
# RESET BUTTON
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.clear()
    st.rerun()
