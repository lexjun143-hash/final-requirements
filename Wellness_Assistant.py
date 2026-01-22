import streamlit as st
import random

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Emotional Support Chatbot",
    page_icon="💙",
    layout="centered"
)

# --------------------------------------------------------
# KEYWORDS & ANALYSIS DATA (EXPANDED)
# --------------------------------------------------------
EMOTIONS = {
    "stress": ["stress", "pressure", "overwhelmed", "deadline", "too much"],
    "sadness": ["sad", "down", "lonely", "cry", "empty", "hopeless"],
    "fatigue": ["tired", "exhausted", "burnout", "fatigue", "drained"],
    "anxiety": ["anxious", "anxiety", "worried", "panic", "nervous"],
    "anger": ["angry", "mad", "frustrated", "irritated"],
    "fear": ["scared", "afraid", "fearful"],
    "confusion": ["confused", "lost", "uncertain"],
    "motivation_loss": ["unmotivated", "stuck", "no energy"],
    "sleep": ["sleep", "insomnia", "can't sleep", "restless"]
}

TOPICS = {
    "academics": ["school", "exam", "grades", "project", "study"],
    "family": ["family", "parents", "home"],
    "friends": ["friends", "relationship", "social"],
    "future": ["future", "career", "life"],
    "finance": ["money", "tuition", "budget", "broke"],
    "work": ["job", "work", "shift"],
    "self_esteem": ["confidence", "insecure", "hate myself"]
}

INTENSIFIERS = [
    "very", "too", "always", "never", "can't", "anymore", "really", "extremely"
]

# --------------------------------------------------------
# MESSAGE ANALYSIS
# --------------------------------------------------------
def analyze_message(text):
    text = text.lower()
    emotions, topics = [], []
    intensity = any(i in text for i in INTENSIFIERS)

    for e, words in EMOTIONS.items():
        if any(w in text for w in words):
            emotions.append(e)

    for t, words in TOPICS.items():
        if any(w in text for w in words):
            topics.append(t)

    return emotions or ["general"], topics, intensity

# --------------------------------------------------------
# REFLECTION
# --------------------------------------------------------
def reflect_message(emotions, topics, intensity):
    lines = ["From what you shared, it sounds like:"]

    for e in emotions:
        lines.append(f"• you’re experiencing **{e.replace('_', ' ')}**")

    for t in topics:
        lines.append(f"• this connects to **{t.replace('_', ' ')}**")

    if intensity:
        lines.append("• these feelings feel especially strong right now")

    return "\n".join(lines)

# --------------------------------------------------------
# ADVICE ENGINE
# --------------------------------------------------------
def give_advice(emotions, depth):
    advice_bank = {
        "stress": [
            "Try focusing on one small task at a time.",
            "Pausing briefly can reduce mental overload.",
            "You don’t need to solve everything today."
        ],
        "sadness": [
            "It’s okay to feel this way.",
            "Comforting routines can help during low moments.",
            "You deserve patience and kindness."
        ],
        "fatigue": [
            "Your body may be asking for rest.",
            "Short breaks still count as recovery.",
            "Rest is productive."
        ],
        "anxiety": [
            "Slow breathing can calm your nervous system.",
            "Grounding yourself in the present may help.",
            "You are safe right now."
        ],
        "general": [
            "You’re doing the best you can.",
            "One step at a time is enough.",
            "You deserve support."
        ]
    }

    responses = []
    for e in emotions:
        tips = advice_bank.get(e, advice_bank["general"])
        responses.append(f"💡 {tips[min(depth, len(tips) - 1)]}")

    return "\n".join(responses)

# --------------------------------------------------------
# ADVANCED FOLLOW-UP PROMPTS
# --------------------------------------------------------
FOLLOW_UP_BANK = {
    "reflection": [
        "Does this describe how you’re feeling?",
        "Did I understand you correctly?",
        "Does any part of this stand out to you?"
    ],
    "clarification": [
        "What part feels hardest right now?",
        "When did this start to feel this way?",
        "Is there something specific triggering this?"
    ],
    "coping": [
        "What have you tried so far to cope?",
        "What usually helps, even a little?",
        "Would you like to explore a small next step?"
    ],
    "satisfaction": [
        "Is this helping you feel a bit lighter?",
        "Do you feel heard right now?",
        "Would you like me to keep listening or give advice?"
    ]
}

def choose_follow_up(turn_count):
    if turn_count < 2:
        category = "reflection"
    elif turn_count < 4:
        category = "clarification"
    elif turn_count < 6:
        category = "coping"
    else:
        category = "satisfaction"

    return random.choice(FOLLOW_UP_BANK[category])

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.title("💙 Campus Emotional Support Chatbot")
st.caption("A space where you can talk freely and be understood.")

# --------------------------------------------------------
# SESSION STATE (EXPANDED)
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_reply" not in st.session_state:
    st.session_state.first_reply = True

if "depth" not in st.session_state:
    st.session_state.depth = 0

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = []

if "topic_history" not in st.session_state:
    st.session_state.topic_history = []

# --------------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if prompt := st.chat_input("You can share anything here…"):

    st.session_state.turn_count += 1
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Understanding..."):

            if st.session_state.first_reply:
                response = "Hello! 👋😊\n\nWhat can I do for you today?"
                st.session_state.first_reply = False
            else:
                emotions, topics, intensity = analyze_message(prompt)
                st.session_state.emotion_history.extend(emotions)
                st.session_state.topic_history.extend(topics)

                reflection = reflect_message(emotions, topics, intensity)
                advice = give_advice(emotions, st.session_state.depth)
                follow_up = choose_follow_up(st.session_state.turn_count)

                response = (
                    f"{reflection}\n\n"
                    f"{advice}\n\n"
                    f"{follow_up}\n\n"
                    "You can take your time — I’m here with you."
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
