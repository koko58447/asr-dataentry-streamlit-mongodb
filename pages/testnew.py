import streamlit as st
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
import speech_recognition as sr
from pymongo import MongoClient
import pandas as pd


# Initialize session_state
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'father_name' not in st.session_state:
    st.session_state.father_name = ""
if 'mother_name' not in st.session_state:
    st.session_state.mother_name = ""
if 'nrc' not in st.session_state:
    st.session_state.nrc = ""
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'note' not in st.session_state:
    st.session_state.note = ""

for field in ['name', 'father_name', 'mother_name', 'nrc', 'address', 'note']:
    if f"audio_key_{field}" not in st.session_state:
        st.session_state[f"audio_key_{field}"] = 0

# Function to handle recording and updating a specific field
def record_audio_and_update(field_name):
    audio = audio_recorder(
        text="",
        recording_color="#FF0000",
        neutral_color="#000000",
        icon_size="2x",
        key=f"audio_recorder_{field_name}_{st.session_state[f'audio_key_{field_name}']}"
    )

    if audio is not None:
        try:
            audio_file = BytesIO(audio)
            r = sr.Recognizer()

            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="my-MM")
                st.session_state[field_name] = text

                # Refresh key to allow next recording
                st.session_state[f"audio_key_{field_name}"] += 1
                st.rerun()

        except sr.UnknownValueError:
            st.error("error")
        except sr.RequestError as e:
            st.error(f"error")

# MongoDB Connection
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])


# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["voice_form_db"]
collection = db["users"]

# Save Data to MongoDB
def save_to_mongodb(data):
    collection.insert_one(data)

def clean_text():
    st.session_state.name=""
    st.session_state.father_name=""
    st.session_state.mother_name=""
    st.session_state.nrc=""
    st.session_state.address=""
    st.session_state.note=""
    st.rerun()


st.subheader("🎙️ Voice Form - New Entry")
updated_data = {}

labels = {
    "name": "အမည်",
    "father_name": "အဖအမည်",
    "mother_name": "အမိအမည်",
    "nrc": "မှတ်ပုံတင်အမှတ်",
    "address": "နေရပ်လိပ်စာ",
    "note": "မှတ်ချက်"
}

for field, label in labels.items():
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(label, value=st.session_state[field], key=f"{field}_input" ,icon="♻️")
        updated_data[field] = user_input
    with col2:
        st.write("<br>", unsafe_allow_html=True)
        record_audio_and_update(field)

if st.button("💾 သိမ်းဆည်းမည်"):
    save_to_mongodb(updated_data)
    st.success("✅ သိမ်းဆည်းပြီးပြီ!")
    clean_text()

