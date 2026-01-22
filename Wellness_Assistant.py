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

    intents = {
        "features": ["what can you do", "help", "features", "services"],
        "stress": ["stress", "anxious", "anxiety", "overwhelmed", "pressure"],
        "sad": ["sad", "down", "lonely", "depressed"],
        "fatigue": ["tired", "fatigue", "exhausted", "burnout"],
        "sleep": ["sleep", "insomnia", "can't sleep"],
        "headache": ["headache", "head hurts", "body pain", "neck pain"],
        "motivation": ["unmotivated", "no motivation", "lazy", "burned out"],
        "study": ["study", "exam", "deadline", "school", "academic"],
        "routine": ["routine", "habit", "daily", "lifestyle"],
        "emergency": ["suicide", "kill myself", "hurt myself", "die"]
    }

    for intent, keywords in intents.items():
        if any(word in text for word in keywords):
            return intent

    return "general"

# --------------------------------------------------------
# RESPONSE ENGINE
# --------------------------------------------------------
def handle_intent(intent):
    responses = {
        "features": (
            "I can help you with:\n\n"
            "• Stress, anxiety, and emotional support\n"
            "• Sleep and fatigue concerns\n"
            "• Study pressure and burnout\n"
            "• Motivation and focus\n"
            "• Healthy routines and self-care habits\n\n"
            "Just tell me what you’re experiencing."
        ),

        "stress": (
            "That sounds stressful, and it’s completely understandable. 💛\n\n"
            "Let’s slow things down a bit:\n"
            "• Take 5 slow, deep breaths\n"
            "• Focus on one task at a time\n"
            "• Give yourself short breaks\n\n"
            "Would you like help managing stress right now or planning your tasks?"
        ),

        "sad": (
            "I’m really glad you shared that. 💙\n\n"
            "Feeling sad or lonely can happen to anyone.\n"
            "Some gentle steps:\n"
            "• Talk to someone you trust\n"
            "• Do something comforting\n"
            "• Be kind to yourself\n\n"
            "If this feeling lasts for a long time, professional support can really help."
        ),

        "fatigue": (
            "Feeling exhausted can take a toll. 😴\n\n"
            "You might try:\n"
            "• Getting enough sleep\n"
            "• Drinking water regularly\n"
            "• Taking short breaks\n"
            "• Reducing screen time\n\n"
            "Has this been going on for days or weeks?"
        ),

        "sleep": (
            "Sleep issues are very common among students.\n\n"
            "Try these tonight:\n"
            "• Go to bed at the same time\n"
            "• Avoid screens 1 hour before sleep\n"
            "• Keep your room quiet and dim\n\n"
            "Would you like help creating a bedtime routine?"
        ),

        "headache": (
            "Headaches can be uncomfortable. 🤕\n\n"
            "You may try:\n"
            "• Drinking water\n"
            "• Resting your eyes\n"
            "• Stretching your neck and shoulders\n\n"
            "If headaches are frequent or severe, seeking professional advice is important."
        ),

        "motivation": (
            "Losing motivation happens, especially when you’re tired or overwhelmed.\n\n"
            "Let’s start small:\n"
            "• Pick one easy task\n"
            "• Set a short time limit\n"
            "• Reward yourself afterward\n\n"
            "Want help breaking something down?"
        ),

        "study": (
            "Academic pressure can be really heavy. 🎓\n\n"
            "Helpful strategies:\n"
            "• Break study time into short sessions\n"
            "• Prioritize urgent tasks\n"
            "• Take planned breaks\n\n"
            "What subject or task are you working on?"
        ),

        "routine": (
            "A simple routine can make a big difference. 🌱\n\n"
            "A healthy day often includes:\n"
            "• Consistent sleep\n"
            "• Balanced meals\n"
            "• Light physical activity\n"
            "• Time to relax\n\n"
            "Would you like me to help you create a simple routine?"
        ),

        "emergency": (
            "I’m really concerned about your safety. ❤️\n\n"
            "You’re not alone, and help is available.\n"
            "Please consider reaching out to a trusted person or a professional right away.\n\n"
            "If you’re in immediate danger, please contact local emergency services."
        ),

        "general": (
            "I’m here to help and listen. 😊\n\n"
            "You can talk to me about stress, sleep, motivation, "
            "school pressure, or general wellness. What’s on your mind?"
        )
    }

    return responses.get(intent, responses["general"])

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("💬 Campus Self-Care & Wellness Chatbot")
st.caption(
    "A supportive, customer-service–style chatbot for student wellness "
    "and everyday challenges."
)

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

            # FIRST CHAT RULE (STRICT)
            if not st.session_state.first_reply_done:
                response = (
                    "Hello! 👋😊\n\n"
                    "What can I do for you today?"
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
