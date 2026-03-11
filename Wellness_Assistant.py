import streamlit as st
import pandas as pd
import random
import snowflake.connector

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------

st.set_page_config(
    page_title="Campus Wellness Support Chatbot",
    page_icon="💙",
    layout="centered"
)

st.title("💙 Campus Wellness Support Chatbot")
st.caption("A supportive space for students to talk about emotions, stress, and personal challenges.")

# --------------------------------------------------------
# CONNECT TO SNOWFLAKE
# --------------------------------------------------------

conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)

# --------------------------------------------------------
# LOAD DATASET FROM SNOWFLAKE
# --------------------------------------------------------

@st.cache_data
def load_dataset():

    query = """
    SELECT EMOTION, TOPIC, KEYWORD, RESPONSE
    FROM CHATBOT.PUBLIC.DATASET
    """

    df = pd.read_sql(query, conn)

    # convert to lowercase for matching
    df["EMOTION"] = df["EMOTION"].str.lower()
    df["TOPIC"] = df["TOPIC"].str.lower()
    df["KEYWORD"] = df["KEYWORD"].str.lower()

    return df


dataset = load_dataset()

# --------------------------------------------------------
# DEFAULT RESPONSES
# --------------------------------------------------------

default_responses = [
    "I'm here to listen. Could you share more about what you're feeling?",
    "It sounds like something is bothering you. I'm here with you.",
    "Your feelings are valid. Tell me more about your situation.",
    "Sometimes talking helps. What would you like to share today?"
]

# --------------------------------------------------------
# CHAT MEMORY
# --------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --------------------------------------------------------
# USER INPUT
# --------------------------------------------------------

user_input = st.chat_input("How are you feeling today?")

if user_input:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    user_text = user_input.lower()

    # --------------------------------------------------------
    # FIND MATCHING RESPONSES
    # --------------------------------------------------------

    matched_rows = dataset[
        dataset["EMOTION"].apply(lambda x: x in user_text) |
        dataset["TOPIC"].apply(lambda x: x in user_text) |
        dataset["KEYWORD"].apply(lambda x: x in user_text)
    ]

    # --------------------------------------------------------
    # SELECT BOT RESPONSE
    # --------------------------------------------------------

    if not matched_rows.empty:
        bot_response = random.choice(matched_rows["RESPONSE"].tolist())
    else:
        bot_response = random.choice(default_responses)

    # --------------------------------------------------------
    # DISPLAY BOT RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response
    })

    with st.chat_message("assistant"):
        st.write(bot_response)

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------

with st.sidebar:

    st.header("About the System")

    st.write("""
This chatbot provides wellness support for students by analyzing
emotions and topics mentioned in user messages.

The responses are dynamically retrieved from a dataset stored in Snowflake.
""")

    st.subheader("System Features")

    st.write("✔ Emotion-based responses")
    st.write("✔ Topic-based support")
    st.write("✔ Keyword detection")
    st.write("✔ Dataset-driven chatbot")
    st.write("✔ Randomized response selection")

    st.divider()

    st.caption("Developed for academic research and student wellness.")
