import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile
from io import BytesIO
from audio_recorder_streamlit import audio_recorder

# Page config
# st.set_page_config(page_title="🎙️ Speech to Text", layout="centered")
st.title("🎙️ Automatic Speech Recognition with Streamlit")

st.markdown("""
<style>
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for converting audio
def transcribe_audio(audio_file_path):
    print(f"Transcribing audio file: {audio_file_path}")
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="my-MM")  # Myanmar support
            return text
    except sr.UnknownValueError:
        return "⚠️ error"
    except sr.RequestError as e:
        return f"⚠️ error; {e}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# File Upload Section
st.header("📁 Upload Audio File")
uploaded_file = st.file_uploader("WAV သို့မဟုတ် MP3 ဖိုင်ကို upload လုပ်ပါ", type=["wav", "mp3"])
st.audio(uploaded_file, format="audio/wav")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        if uploaded_file.type == "audio/mp3":
            audio = AudioSegment.from_mp3(uploaded_file)
            audio.export(tmpfile.name, format="wav")
        else:
            tmpfile.write(uploaded_file.getvalue())

        audio_path = tmpfile.name


    if st.button("🎤 Transcribe Uploaded Audio"):
        st.info("Processing...")
        result = transcribe_audio(audio_path)
        st.success("✅ Result:")
        st.write(result)

# Real-time Recording Section
st.header("🎙️ Streamlit Audio Recorder + Speech Recognition")
# Record audio from user
# audio = st_audiorec()
# audio = audio_recorder(text="",recording_color="#FF0000", neutral_color="#000000", icon_size="4x")
# st.audio(audio, format="audio/wav")

audio=st.audio_input("Record your voice")

if audio is not None:

    # st.audio(audio, format='audio/wav')
    # Convert bytes to file-like object
    # audio_file = BytesIO(audio)
    audio_file = audio

    # Recognize speech using Google's Web API
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="my-MM")
            st.success(f"Recognized Text: {text}")
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
