import streamlit as st
import random

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Campus Wellness Support Chatbot",
    page_icon="💙",
    layout="centered"
)

# --------------------------------------------------------
# KEYWORDS & ANALYSIS DATA (EXPANDED)
# --------------------------------------------------------

EMOTIONS = {
    "stress": ["stress", "pressure", "overwhelmed", "too much", "deadline"],
    "sadness": ["sad", "down", "lonely", "cry", "empty", "hopeless"],
    "anxiety": ["anxious", "worried", "panic", "nervous", "overthinking"],
    "anger": ["angry", "mad", "frustrated", "irritated", "annoyed"],
    "fear": ["scared", "afraid", "terrified", "unsafe"],
    "guilt": ["guilty", "regret", "ashamed", "my fault"],
    "fatigue": ["tired", "exhausted", "burnout", "drained"],
    "numbness": ["numb", "nothing", "emotionless"],
    "confusion": ["confused", "lost", "uncertain"],
    "motivation": ["unmotivated", "lazy", "stuck", "giving up"],
    "self_doubt": ["not good enough", "failure", "useless", "hate myself"]
}

TOPICS = {
    "academics": ["school", "exam", "grades", "project", "study"],
    "time": ["time", "late", "deadline", "schedule"],
    "finance": ["money", "tuition", "fees", "broke"],
    "family": ["family", "parents", "home"],
    "friends": ["friends", "friendship", "peer"],
    "relationships": ["relationship", "breakup", "partner"],
    "future": ["future", "career", "life", "purpose"],
    "health": ["health", "body", "sick", "unwell"]
}

INTENSIFIERS = ["very", "too", "always", "never", "can't", "anymore"]
DISTRESS_PHRASES = [
    "i can't handle", "i give up", "nothing helps",
    "i'm done", "what's the point"
]

# --------------------------------------------------------
# ANALYZE USER MESSAGE
# --------------------------------------------------------
def analyze_message(text):
    text = text.lower()
    emotions = []
    topics = []

    intensity = any(word in text for word in INTENSIFIERS)
    distress = any(phrase in text for phrase in DISTRESS_PHRASES)

    for emo, words in EMOTIONS.items():
        if any(w in text for w in words):
            emotions.append(emo)

    for topic, words in TOPICS.items():
        if any(w in text for w in words):
            topics.append(topic)

    if not emotions:
        emotions.append("general")

    return emotions, topics, intensity, distress

# --------------------------------------------------------
# RESPONSE GENERATOR
# --------------------------------------------------------
def generate_response(user_text, first_chat=False):
    emotions, topics, intense, distress = analyze_message(user_text)

    if first_chat:
        return (
            "Hello! 👋 I’m here to support your well-being.\n\n"
            "You can talk to me about stress, school pressure, emotions, "
            "personal struggles, or anything that’s been weighing on you.\n\n"
            "How can I help you today?"
        )

    response = ""

    # Empathy
    if "sadness" in emotions:
        response += "It sounds like you’re feeling really down, and that’s not easy. 💙\n\n"
    if "stress" in emotions:
        response += "You seem under a lot of pressure right now. That can feel overwhelming.\n\n"
    if "anxiety" in emotions:
        response += "I can sense some anxiety in what you shared. Let’s slow things down together.\n\n"
    if "anger" in emotions:
        response += "Feeling frustrated like this can be exhausting. It’s okay to acknowledge it.\n\n"
    if "self_doubt" in emotions:
        response += "You might be being very hard on yourself right now. You deserve compassion too.\n\n"

    # Topic-based advice
    if "academics" in topics:
        response += (
            "School pressure can really pile up. Breaking tasks into smaller steps "
            "and giving yourself short breaks can help reduce that weight.\n\n"
        )
    if "future" in topics:
        response += (
            "Uncertainty about the future is very common, especially during college. "
            "You don’t need to have everything figured out right now.\n\n"
        )
    if "relationships" in topics:
        response += (
            "Relationships can deeply affect our emotions. Talking about what you’re feeling "
            "instead of holding it in can make a difference.\n\n"
        )

    # Intensity & distress handling
    if intense:
        response += (
            "It sounds like these feelings have been building up for a while. "
            "You don’t have to deal with everything all at once.\n\n"
        )

    if distress:
        response += (
            "I’m really glad you reached out instead of keeping this to yourself. "
            "You matter, and your feelings deserve attention.\n\n"
        )

    # Follow-up encouragement
    response += random.choice([
        "If you’re comfortable, you can tell me more about what’s been going on.",
        "What part of this feels hardest for you right now?",
        "I’m listening—feel free to share whatever you need.",
        "Would you like help thinking through one small step forward?"
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
if user_input := st.chat_input("Type how you're feeling..."):
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = generate_response(
            user_input,
            first_chat=st.session_state.first_chat
        )
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    st.session_state.first_chat = False

# --------------------------------------------------------
# RESET BUTTON
# --------------------------------------------------------
if st.button("🔄 Reset Chat"):
    st.session_state.messages = []
    st.session_state.first_chat = True
    st.success("Chat reset. You can start again.")
