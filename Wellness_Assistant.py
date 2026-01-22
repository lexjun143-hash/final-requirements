import streamlit as st
import random
import re

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Wellness Support Chatbot",
    page_icon="💙",
    layout="centered"
)

# --------------------------------------------------------
# GREETING KEYWORDS (FIRST CHAT ONLY)
# --------------------------------------------------------
GREETINGS = [
    "hi", "hello", "hey",
    "good morning", "good afternoon", "good evening"
]

# --------------------------------------------------------
# KEYWORDS & ANALYSIS DATA (FULL)
# --------------------------------------------------------

EMOTIONS = {
    "stress": ["stress", "pressure", "overwhelmed", "deadline", "burnout"],
    "sadness": ["sad", "down", "lonely", "cry", "hopeless"],
    "anxiety": ["anxious", "worried", "panic", "nervous"],
    "anger": ["angry", "mad", "frustrated", "annoyed"],
    "fatigue": ["tired", "exhausted", "drained"],
    "self_doubt": ["not good enough", "failure", "useless"],
    "numbness": ["numb", "empty", "emotionless"]
}

TOPICS = {
    "academics": ["school", "exam", "grades", "project", "study"],
    "time": ["time", "schedule", "deadline", "late"],
    "finance": ["money", "tuition", "fees"],
    "family": ["family", "parents", "home"],
    "relationships": ["relationship", "breakup", "partner"],
    "future": ["future", "career", "life"],
    "health": ["health", "body", "unwell"]
}

INTENSIFIERS = [
    "very", "too", "always", "never",
    "can't", "anymore", "really"
]

DISTRESS_PATTERNS = [
    "i can't handle", "i give up",
    "nothing helps", "i'm done",
    "what's the point"
]

# --------------------------------------------------------
# MESSAGE ANALYSIS
# --------------------------------------------------------
def analyze_message(text):
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)

    emotions, topics = [], []

    intensity = any(word in words for word in INTENSIFIERS)
    distress = any(phrase in text_lower for phrase in DISTRESS_PATTERNS)

    for emo, keys in EMOTIONS.items():
        if any(k in text_lower for k in keys):
            emotions.append(emo)

    for topic, keys in TOPICS.items():
        if any(k in text_lower for k in keys):
            topics.append(topic)

    if not emotions:
        emotions.append("general")

    return words, emotions, topics, intensity, distress, len(words)

# --------------------------------------------------------
# RESPONSE GENERATOR
# --------------------------------------------------------
def generate_response(user_text, first_chat):
    text_lower = user_text.lower()

    # FIRST CHAT GREETING ONLY
    if first_chat and any(greet in text_lower for greet in GREETINGS):
        return (
            "Hello! 👋 Welcome.\n\n"
            "I’m here to support your well-being. You can talk to me about stress, "
            "school pressure, emotions, relationships, or anything on your mind.\n\n"
            "How can I help you today?"
        )

    words, emotions, topics, intense, distress, length = analyze_message(user_text)

    reflection = " ".join(words[:10]) + "..." if length > 10 else user_text

    response = (
        f"Thank you for sharing this.\n\n"
        f"From what you said about **“{reflection}”**, "
        f"it sounds like this is something meaningful for you.\n\n"
    )

    if "general" in emotions:
        response += "Even if it’s hard to explain, what you’re feeling still matters.\n\n"
    if "sadness" in emotions:
        response += "Feeling sad like this can be heavy to carry.\n\n"
    if "stress" in emotions:
        response += "That pressure can really build up over time.\n\n"
    if "anxiety" in emotions:
        response += "It sounds like your thoughts may be racing.\n\n"
    if "anger" in emotions:
        response += "Frustration like this can be exhausting.\n\n"
    if "self_doubt" in emotions:
        response += "You might be judging yourself more harshly than you deserve.\n\n"

    if "academics" in topics:
        response += (
            "Academic stress is very common. Breaking tasks into smaller steps "
            "can make things feel more manageable.\n\n"
        )

    if intense:
        response += (
            "These feelings seem strong right now. Let’s take things one step at a time.\n\n"
        )

    if distress:
        response += (
            "I’m really glad you reached out. You don’t have to carry this alone.\n\n"
        )

    if length < 4:
        response += "If you want, you can share a bit more.\n\n"

    response += random.choice([
        "What part of this feels hardest right now?",
        "Do you want to tell me more about what led to this?",
        "I’m here — you can keep sharing.",
        "What do you feel you need most at the moment?"
    ])

    return response

# --------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_chat" not in st.session_state:
    st.session_state.first_chat = True

# --------------------------------------------------------
# UI
# --------------------------------------------------------
st.title("💙 Campus Wellness Support Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# CHAT INPUT
# --------------------------------------------------------
if user_input := st.chat_input("Share what’s on your mind…"):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = generate_response(user_input, st.session_state.first_chat)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.first_chat = False

# --------------------------------------------------------
# RESET BUTTON
# --------------------------------------------------------
if st.button("🔄 Reset Chat"):
    st.session_state.messages = []
    st.session_state.first_chat = True
    st.success("Chat cleared. You can start again.")
