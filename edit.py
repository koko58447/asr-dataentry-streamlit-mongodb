import streamlit as st
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
import speech_recognition as sr
from pymongo import MongoClient
import os
import module as md
from PIL import Image
import random

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
    }
    .stTextInput input {
        border-radius: 5px;
        padding: 8px;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
    }
    .stDataFrame {
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 10px;
    }
            
    .button-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .stButton button {
        width: 100% !important;
        padding: 0.5em 1em !important;
        text-align: center;
        border-radius: 6px !important;
    }
    .stDownloadButton button {
        width: 100% !important;
        padding: 0.5em 1em !important;
        text-align: center;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# uploads ဖိုလ်ဒါ မရှိရင် ဖန်တီးမယ်
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def deleteImg(img_path):
    if img_path is not None :       
        img_path = str(img_path)
        full_path = os.path.join(os.getcwd(), img_path)        
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                st.error(f"⚠️ ဓာတ်ပုံဖျက်ရာတွင် အမှားဖြစ်ပွားခဲ့ပါသည်: {e}")

data=""
collection=md.get_collection("users")
if "selected_id" not in st.session_state:
    st.info("⚠️ အချက်အလက်ရွေးပေးပါ")
else:
    doc_id = st.session_state.selected_id    
    data = collection.find_one({"_id": doc_id})    

if data:
    st.subheader("🖋️ အချက်အလက်ပြင်ဆင်ခြင်း")
    
    if 'name' not in st.session_state:
        st.session_state.name =  data.get("name", "")
    if 'father_name' not in st.session_state:
        st.session_state.father_name =  data.get("father_name", "")
    if 'mother_name' not in st.session_state:
        st.session_state.mother_name = data.get("mother_name", "")
    if 'nrc' not in st.session_state:
        st.session_state.nrc =  data.get("nrc", "")
    if 'address' not in st.session_state:
        st.session_state.address = data.get("address", "")
    if 'punish' not in st.session_state:
        st.session_state.punish =  data.get("punish", "")
    if 'img' not in st.session_state:
        st.session_state.img =  data.get("pic_path", None)            
    
    img_path=data.get("pic_path", None)
    labels = {
        "name": "အမည်",
        "father_name": "အဖအမည်",
        "mother_name": "အမိအမည်",
        "nrc": "မှတ်ပုံတင်အမှတ်",
        "address": "နေရပ်လိပ်စာ",
        "punish": "ပြစ်မှုအမျိုးအစား"
    }

    # Create a dictionary to hold the updated values
    updated_data = {}
    img=None

    cola, colb = st.columns([3, 2])
    with cola:
        col1,col2=st.columns([5,1])
        with col1:
            name=st.text_input("အမည်",value=st.session_state['name'],key="name_input",icon="♻️")
        with col2:
            col2.write("<br>", unsafe_allow_html=True)
            md.record_audio_and_update("name")
        with col1:
            father_name=st.text_input("အဖအမည်",value=st.session_state['father_name'],key="father_name_input",icon="♻️")
        with col2:
            col2.write("<br>", unsafe_allow_html=True)
            md.record_audio_and_update("father_name")
        with col1:
            mother_name=st.text_input("အမိအမည်",value=st.session_state['mother_name'],key="mother_name_input",icon="♻️")
        with col2:
            col2.write("<br>", unsafe_allow_html=True)
            md.record_audio_and_update("mother_name")
        with col1:
            nrc=st.text_input("မှတ်ပုံတင်အမှတ်",value=st.session_state['nrc'],key="nrc_input",icon="♻️")
        with col2:
            col2.write("<br>", unsafe_allow_html=True)
            md.record_audio_and_update("nrc")
        with col1:
            punish=st.text_input("ပြစ်မှုအမျိုးအစား",value=st.session_state['punish'],key="punish_input",icon="♻️")
        with col2:
            col2.write("<br>", unsafe_allow_html=True)
            md.record_audio_and_update("punish")
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
            if st.button("💾 သိမ်းမည်"): 

                img1 = st.session_state.get("img1", None)
                img = st.session_state.get("img", None)
                pic_path = None
                print(st.session_state.chk_edit)
                # Image ရှိလားစစ်
                if img1 is not None:
                    # 6 လုံးကိန်းပြည့် random ဖြစ်စေရန်
                    random_digits = ''.join(str(random.randint(0, 9)) for _ in range(6))
                    # session_state ကနေ အမည်ယူပြီး filename ဖန်တီး
                    filename = f"image_edit_{random_digits}.jpg"
                    pic_path = os.path.join(UPLOAD_FOLDER, filename)

                    # Image ကိုသိမ်း
                    with open(pic_path, "wb") as f:
                        f.write(img1.getvalue())

                    # Add to data
                    updated_data["pic_path"] = pic_path
                    st.success(f"📸 ဓာတ်ပုံကို `{pic_path}` သို့သိမ်းပြီးပြီ!")
                    deleteImg(img)
                 
                collection.update_one(
                    {"_id": doc_id},
                    {"$set": updated_data}
                )
                md.delete_session()
                st.success("✅ ပြင်ပြီးပြီ။")
                st.switch_page("pages/show.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
            if st.button("🔙 နောက်သို့"):
               md.delete_session()
               st.switch_page("pages/show.py")
            st.markdown('</div>', unsafe_allow_html=True)
    with colb:     
        img_path=""
        if 'img' in st.session_state and st.session_state.img is not None:
            st.image(st.session_state.img, caption="ဓာတ်ပုံ", use_container_width=True)           
        else:
            del st.session_state["img"]
            st.info("⚠️ ဓာတ်ပုံမရှိပါ။")
      
        with st.expander("Photo"):    
            pic = st.camera_input("📷 ဓာတ်ပုံရိုက်ရန်", key="camera_input")
            bro = st.file_uploader("📷 ဓာတ်ပုံတင်ရန်", type=["jpg", "jpeg", "png"], key="upload_input")
            # ဓာတ်ပုံကို img ထဲသို့သိမ်း
            img = None            
            if pic:
                img = pic
            elif bro:
                img = bro
            if img is not None:
                st.session_state['img1'] = img
                st.image(st.session_state.img1, caption="ဓာတ်ပုံ", use_container_width=True)
                st.success("📷 ဓာတ်ပုံကိုဘယ်သို့သိမ်းပြီးပြီ။")
  