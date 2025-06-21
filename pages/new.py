import streamlit as st
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
import speech_recognition as sr
from pymongo import MongoClient
import os
import module as md
import random

# ဓာတ်ပုံသိမ်းမယ့် folder ဖန်တီး
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# md.delete_session()

# Initialize session_state
for field in ['name', 'father_name', 'mother_name', 'nrc', 'address', 'punish','name_1']:
    if field not in st.session_state:
        st.session_state[field] = ""
    if f"audio_key_{field}" not in st.session_state:
        st.session_state[f"audio_key_{field}"] = 0

# MongoDB Connection
collection = md.get_collection("users")

# Save Data to MongoDB
def save_to_mongodb(data):
    collection.insert_one(data)

def clean_text():
    for field in ['name', 'father_name', 'mother_name', 'nrc', 'address', 'punish','name_1']:
        st.session_state[field] = ""
    # Image widgets တွေကို reset (မဖျက်ဘဲ session_state မှာမရှိရင် skip လုပ်)
    if "camera_input" in st.session_state:
        del st.session_state["camera_input"]
    if "upload_input" in st.session_state:
        del st.session_state["upload_input"]
    if "img" in st.session_state:
        del st.session_state["img"]
    # Rerun
    st.rerun()
    
# UI Layout
st.subheader("🎙️ Voice Form - New Entry")

updated_data = {}

labels = {
    "name": "အမည်",
    "father_name": "အဖအမည်",
    "mother_name": "အမိအမည်",
    "nrc": "မှတ်ပုံတင်အမှတ်",
    "address": "နေရပ်လိပ်စာ",
    "punish": "ပြစ်မှုအမျိုးအစား"
}

cola, colb = st.columns([3, 2])
with cola:
    col1,col2=st.columns([5,1])
    with col1:
        name=st.text_input("အမည်",value=st.session_state['name'],key="name_input",icon="♻️")
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("name")
    col1,col2=st.columns([5,1])
    with col1:
        father_name=st.text_input("အဖအမည်",value=st.session_state['father_name'],key="father_name_input",icon="♻️")
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("father_name")
    col1,col2=st.columns([5,1])
    with col1:
        mother_name=st.text_input("အမိအမည်",value=st.session_state['mother_name'],key="mother_name_input",icon="♻️")
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("mother_name")
    col1,col2=st.columns([5,1])
    with col1:
        nrc=st.text_input("မှတ်ပုံတင်အမှတ်",value=st.session_state['nrc'],key="nrc_input",icon="♻️")
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("nrc")
    col1,col2=st.columns([5,1])
    with col1:
        punish=st.text_input("ပြစ်မှုအမျိုးအစား",value=st.session_state['punish'],key="punish_input",icon="♻️")
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("punish")
    col1,col2=st.columns([5,1])
    with col1:
        address=st.text_area("နေရပ်လိပ်စာ",value=st.session_state['address'],key="address_input")     
    with col2:
        col2.write("<br>", unsafe_allow_html=True)
        md.record_audio_and_update("address")

    updated_data = {
        "name": name,
        "father_name": father_name,
        "mother_name": mother_name,
        "nrc": nrc,
        "address": address,
        "punish": punish
    }

    if st.button("💾 သိမ်းဆည်းမည်"):
        # img ကို sidebar ကနေယူ
        img = st.session_state.get("img", None)

        pic_path = None

        # Image ရှိလားစစ်
        if img is not None:
            random_digits = ''.join(str(random.randint(0, 9)) for _ in range(6))
            filename = f"image_{random_digits}.jpg"            
            pic_path = os.path.join(UPLOAD_FOLDER, filename)

            # Image ကိုသိမ်း
            with open(pic_path, "wb") as f:
                f.write(img.getvalue())

            # Add to data
            updated_data["pic_path"] = pic_path

            st.success(f"📸 ဓာတ်ပုံကို `{pic_path}` သို့သိမ်းပြီးပြီ!")

        if updated_data is None:
            st.error("⚠️ အမည် ထည့်ပေးပါ။")           
        else:
             # Save to MongoDB
            save_to_mongodb(updated_data)
            clean_text()
            st.success("✅ သိမ်းဆည်းပြီးပြီ။")
with colb:
    with st.expander("Photo"):    
        pic = st.camera_input("📷 ဓာတ်ပုံရိုက်ရန်", key="camera_input")
        bro = st.file_uploader("📷 ဓာတ်ပုံတင်ရန်", type=["jpg", "jpeg", "png"], key="upload_input")

        # ဓာတ်ပုံကို img ထဲသို့သိမ်း
        img = None
        if pic:
            img = pic
        elif bro:
            img = bro
        st.session_state['img'] = img  # session_state မှာသိမ်းထား
    if 'img' in st.session_state and st.session_state.img is not None:
        st.write("📷 ဓာတ်ပုံကြည့်ရန်")
        st.image(st.session_state.img, caption="ဓာတ်ပုံ", use_container_width=True,)
        st.success("📷 ဓာတ်ပုံကိုဘယ်သို့သိမ်းပြီးပြီ။")
    else:
        st.info("⚠️ ဓာတ်ပုံမရှိပါ။")
    