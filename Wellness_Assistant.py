import streamlit as st

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Emotional Support Chatbot",
    page_icon="💙",
    layout="centered"
)

# --------------------------------------------------------
# KEYWORDS & TOPICS
# --------------------------------------------------------
EMOTIONS = {
    "stress": ["stress", "pressure", "overwhelmed", "deadline", "too much"],
    "sad": ["sad", "down", "lonely", "cry", "empty", "hopeless"],
    "fatigue": ["tired", "exhausted", "burnout", "fatigue"],
    "anxiety": ["anxious", "anxiety", "worried", "panic", "nervous"],
    "sleep": ["sleep", "insomnia", "rest", "can't sleep"]
}

TOPICS = {
    "school": ["school", "class", "exam", "grades", "project"],
    "family": ["family", "parents", "home"],
    "friends": ["friends", "relationship", "people"],
    "future": ["future", "career", "life"],
    "self": ["myself", "me", "identity", "confidence"]
}

INTENSIFIERS = ["very", "too", "always", "never", "can't", "hard"]

# --------------------------------------------------------
# ANALYSIS FUNCTIONS
# --------------------------------------------------------
def analyze_message(text):
    text_lower = text.lower()
    emotions = []
    topics = []
    intensity = False

    for e, words in EMOTIONS.items():
        if any(w in text_lower for w in words):
            emotions.append(e)

    for t, words in TOPICS.items():
        if any(w in text_lower for w in words):
            topics.append(t)

    if any(i in text_lower for i in INTENSIFIERS):
        intensity = True

    return emotions or ["general"], topics, intensity

# --------------------------------------------------------
# REFLECTION ENGINE
# --------------------------------------------------------
def reflect(emotions, topics, intensity):
    lines = ["From what you shared, it sounds like:"]

    for e in emotions:
        lines.append(f"• you’re feeling {e}")

    for t in topics:
        lines.append(f"• this is connected to your {t}")

    if intensity:
        lines.append("• these feelings feel especially strong right now")

    return "\n".join(lines)

# --------------------------------------------------------
# ADVICE ENGINE (VERY DEEP)
# --------------------------------------------------------
def advice(emotions, depth):
    advice_bank = {
        "stress": [
            "Try focusing on one small task at a time.",
            "It may help to pause and remind yourself that you don’t have to solve everything today.",
            "Your effort matters, even when progress feels slow."
        ],
        "sad": [
            "Allow yourself to feel without judging it.",
            "Comforting routines can help during heavy moments.",
            "You’re not weak for feeling this way."
        ],
        "fatigue": [
            "Rest is not laziness — it’s recovery.",
            "Short breaks can help your body reset.",
            "You deserve gentleness, not pressure."
        ],
        "anxiety": [
            "Slow breathing can calm your nervous system.",
            "Grounding yourself in the present may help reduce worry.",
            "You don’t need all the answers right now."
        ],
        "sleep": [
            "Creating a calm bedtime routine can help.",
            "Resting quietly still counts as rest.",
            "Your body will find its rhythm again."
        ],
        "general": [
            "It’s okay to take things one step at a time.",
            "You don’t have to be okay all the time.",
            "You’re doing the best you can right now."
        ]
    }

    responses = []
    for e in emotions:
        tips = advice_bank.get(e, advice_bank["general"])
        responses.append(f"💡 {tips[min(depth, len(tips) - 1)]}")

    return "\n".join(responses)

# --------------------------------------------------------
# FOLLOW-UP ENGINE
# --------------------------------------------------------
def follow_up(depth):
    if depth < 2:
        return "Would you like to tell me more about this?"
    if depth < 4:
        return "Is this helping you so far, or would you like a different kind of support?"
    return "Do you want me to keep listening, or would advice be helpful right now?"

# --------------------------------------------------------
# UI
# --------------------------------------------------------
st.title("💙 Campus Emotional Support Chatbot")
st.caption("A safe space to talk, reflect, and feel supported.")

# --------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first" not in st.session_state:
    st.session_state.first = True

if "depth" not in st.session_state:
    st.session_state.depth = 0

# --------------------------------------------------------
# DISPLAY CHAT
# --------------------------------------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("You can share anything here…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Understanding..."):

            if st.session_state.first:
                response = "Hello! 👋😊\n\nWhat can I do for you today?"
                st.session_state.first = False
                st.session_state.depth = 0
            else:
                emotions, topics, intensity = analyze_message(prompt)
                reflection = reflect(emotions, topics, intensity)
                guidance = advice(emotions, st.session_state.depth)
                follow = follow_up(st.session_state.depth)

                response = (
                    f"{reflection}\n\n"
                    f"{guidance}\n\n"
                    f"{follow}\n\n"
                    "You can correct me if I misunderstood — I’m here to listen."
                )

                st.session_state.depth += 1

            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

# --------------------------------------------------------
# RESET
# --------------------------------------------------------
if st.button("🔄 Restart Conversation"):
    st.session_state.clear()
    st.rerun()
