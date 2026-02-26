import streamlit as st
import random
import re
import pandas as pd

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Wellness Support Chatbot",
    page_icon="💙",
    layout="centered"
)

# --------------------------------------------------------
# LOAD CSV DATASET
# --------------------------------------------------------
@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("wellness_dataset_1000.csv")
        return df
    except:
        return None

df = load_dataset()

# --------------------------------------------------------
# GREETING & GRATITUDE KEYWORDS
# --------------------------------------------------------
GREETINGS = [
    "hi", "hello", "hey",
    "good morning", "good afternoon", "good evening"
]

GRATITUDE_KEYWORDS = [
    "thank you", "thanks", "thank u",
    "appreciate", "grateful", "that helped",
    "i feel better", "much better now"
]

# --------------------------------------------------------
# KEYWORDS & ANALYSIS DATA
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

INTENSIFIERS = ["very", "too", "always", "never", "can't", "anymore", "really"]

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

    emotions = []

    intensity = any(word in words for word in INTENSIFIERS)
    distress = any(phrase in text_lower for phrase in DISTRESS_PATTERNS)
    gratitude = any(g in text_lower for g in GRATITUDE_KEYWORDS)

    for emo, keys in EMOTIONS.items():
        if any(k in text_lower for k in keys):
            emotions.append(emo)

    if not emotions:
        emotions.append("general")

    return words, emotions, intensity, distress, gratitude, len(words)

# --------------------------------------------------------
# DATASET MATCHING FUNCTION
# --------------------------------------------------------
def get_dataset_response(user_text):
    if df is None:
        return None

    text_lower = user_text.lower()

    # Random sample of dataset to improve performance
    sample_df = df.sample(min(100, len(df)))

    for _, row in sample_df.iterrows():
        if row["emotion"] in text_lower:
            return row["response"]

    return None

# --------------------------------------------------------
# RESPONSE GENERATOR
# --------------------------------------------------------
def generate_response(user_text, first_chat):

    text_lower = user_text.lower()

    # FIRST CHAT GREETING
    if first_chat and any(greet in text_lower for greet in GREETINGS):
        return (
            "Hello! 👋 Welcome.\n\n"
            "I’m here to support your well-being. "
            "How can I help you today?"
        )

    words, emotions, intense, distress, gratitude, length = analyze_message(user_text)

    # GRATITUDE RESPONSE
    if gratitude:
        return random.choice([
            "You’re very welcome 💙 I’m really glad I could help.",
            "I’m happy to know the advice helped you.",
            "I’m always here if you need support again."
        ])

    # ----------------------------------------------------
    # 1️⃣ DATASET LAYER (PRIMARY)
    # ----------------------------------------------------
    dataset_reply = get_dataset_response(user_text)
    if dataset_reply:
        return dataset_reply

    # ----------------------------------------------------
    # 2️⃣ RULE-BASED FALLBACK
    # ----------------------------------------------------
    reflection = " ".join(words[:10]) + "..." if length > 10 else user_text

    response = (
        f"Thank you for sharing this.\n\n"
        f"From what you said about “{reflection}”, "
        f"it sounds important.\n\n"
    )

    if "sadness" in emotions:
        response += "Sadness can feel heavy, and it's okay to feel this way.\n\n"

    if "stress" in emotions:
        response += "Stress builds gradually. Small structured steps may help.\n\n"

    if "anxiety" in emotions:
        response += "Anxiety can make thoughts race. Try slow breathing.\n\n"

    if intense:
        response += "These feelings seem strong right now. Let’s slow things down.\n\n"

    if distress:
        response += (
            "I’m really glad you reached out. "
            "If you feel unsafe, please contact a trusted person or professional.\n\n"
        )

    response += random.choice([
        "What feels hardest right now?",
        "Would you like to share more?",
        "I’m here and listening.",
        "What do you need most at this moment?"
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