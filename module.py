# mymodule/audio_utils.py 

import streamlit as st
from pymongo import MongoClient
import pandas as pd
import io
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
import speech_recognition as sr
#whisper model
# from transformers import pipeline,WhisperTokenizer
# import torch
# import librosa
import re 

# connection db with table parameter
def get_collection(table):
    client = MongoClient("mongodb://localhost:27017")
    db = client["voice_form_db"]
    collection = db[table]
    return collection

checkpoint_path = "./gradio/checkpoint-650000/"
pretrained_tokenizer = "./gradio/faster-whisper-large.nb/"

# Move the model to GPU if available
# device = "cuda" if torch.cuda.is_available() else "cpu"

# asr_pipeline=pipeline('automatic-speech-recognition',model=checkpoint_path,tokenizer=pretrained_tokenizer,device=0 if device=="cuda" else -1)

def whisper_asr(audio_path):
    # audio_path = BytesIO(audio_path)
    # stream, sr = librosa.load(audio_path, sr=16000)  # Load as waveform and set sampling rate
    # # Define chunk size (e.g., 10 seconds)
    # chunk_duration = 10  # seconds
    # chunk_samples = chunk_duration * sr

    # transcriptions = []
    # for i in range(0, len(stream), chunk_samples):
    #     audio_chunk = stream[i:i + chunk_samples]
    #     chunk_start_time = i / sr
    #     chunk_end_time = (i + chunk_samples) / sr

    #     transcription = asr_pipeline({
    #         "sampling_rate": sr,
    #         "raw": audio_chunk,
    #         "return_timestamps": True
    #     })
    #     cleaned_text = re.sub(r"[a-z<|>]", "", transcription["text"])
    #     transcriptions.append({
    #             "text": cleaned_text
    #         })
        
    # result=""
    # i=1
    # for segment in transcriptions:
    #     # result+=f"{i}\n{segment['start']} ---> {segment['end']} \n{segment['text']}\n\n\n"
    #     result+=f"{segment['text']}\n\n"
    #     i=i+1

    return result

def online_asr(audio):
   
    try:
        # Convert audio bytes to file-like object
        audio_file = BytesIO(audio)
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        # Recognize Myanmar language
        text = recognizer.recognize_google(audio_data, language="my-MM")
        return text

    except sr.UnknownValueError:
        st.error("⚠️ error။")
    except sr.RequestError as e:
        st.error(f"⚠️ error: {e}")

def record_audio_and_update(field_name):
      # Ensure session_state keys exist
    if f"audio_key_{field_name}" not in st.session_state:
        st.session_state[f"audio_key_{field_name}"] = 0   

    # Audio Recorder UI
   
    audio = audio_recorder(
        text="",
        recording_color="#FF0000",
        neutral_color="#1B7B3DFF",
        icon_size="4x",
        key=f"audio_recorder_{field_name}_{st.session_state[f'audio_key_{field_name}']}"
    )
    

    if audio is not None: 
        text=""
        if st.session_state.model=="own":
            print("own model")
            text=whisper_asr(audio)
        elif st.session_state.model=="online":
            print("online model")
            text=online_asr(audio)
        # # text=online_asr(audio)
        # text=online_asr(audio)
        print(text)
        st.session_state[field_name] = text
        st.session_state[f"audio_key_{field_name}"] += 1
        st.rerun()
            
# Export to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# export to excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

#delete session

def delete_session():
    for key in ['name', 'father_name', 'mother_name', 'nrc', 'address', 'note','img','selected_id']:
            if key in st.session_state:
                del st.session_state[key]