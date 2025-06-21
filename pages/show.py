
import streamlit as st
from pymongo import MongoClient
import pandas as pd
import io
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
import speech_recognition as sr
import module as md
import os

for field in ['name', 'father_name', 'mother_name', 'nrc', 'address', 'punish']:
    if f"audio_key_{field}" not in st.session_state:
        st.session_state[f"audio_key_{field}"] = 0

md.delete_session()

# MongoDB connection
collection = md.get_collection("users")

# Load Data
def load_data():
    items = list(collection.find({}, {"_id": 1, "name": 1, "father_name": 1, "mother_name": 1, "nrc": 1, "address": 1, "punish": 1,"pic_path":1}).sort({"_id":-1}))
    return pd.DataFrame(items)

# Export to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

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

st.subheader("📊 သိမ်းဆည်းထားသောအချက်အလက်များ")

# Auto-refresh toggle
auto_refresh = st.checkbox("🔄 အလိုအလျောက် Refresh လုပ်မည်")
if auto_refresh:
    st.rerun()

df = load_data()

if not df.empty:
    # Add No and Select columns
    df.insert(0, "စဉ်", range(1, len(df) + 1))
    df.insert(1, "ရွေးပါ", False)
    df.columns = [
        "စဉ်",
        "ရွေးပါ",
        "_id",
        "အမည်",
        "အဖအမည်",
        "အမိအမည်",
        "မှတ်ပုံတင်အမှတ်",
        "လိပ်စာ",
        "ပြစ်မှုအမျိုးအစား",
        "img_path"
    ]

    # Filter column options (excluding "စဉ်" and "_id")
    filter_options = [col for col in df.columns.tolist() if col not in ["စဉ်", "_id"]]

    # Search / Filter
    filter_col = st.selectbox("🔍 ရှာဖွေရန် Column", filter_options)
            # Initialize session_state
    if 'search' not in st.session_state:
        st.session_state.search = ""
    col11,col22=st.columns([4,1])
    with col11:            
        filter_val = st.text_input("🔍 ရှာဖွေရန် စာလုံး", value=st.session_state["search"],icon="🔍")
    with col22:
        st.write("<br>",unsafe_allow_html=True)
        md.record_audio_and_update("search")
    
    if filter_val:
        df = df[df[filter_col].astype(str).str.contains(filter_val, case=False, na=False)]

    # Show DataFrame with all columns
    edited_df = st.data_editor(
        df[["စဉ်", "ရွေးပါ", "အမည်", "အဖအမည်", "အမိအမည်", "မှတ်ပုံတင်အမှတ်", "လိပ်စာ", "ပြစ်မှုအမျိုးအစား"]],
        disabled=["စဉ်", "အမည်", "အဖအမည်", "အမိအမည်", "မှတ်ပုံတင်အမှတ်", "လိပ်စာ", "ပြစ်မှုအမျိုးအစား","img_path"],
        use_container_width=True,
        hide_index=True,
    )

    col1,col2, col3, col4 = st.columns([ 1,1, 1, 1])

    with col1:
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        edit_btn = st.button("📝 ပြင်မည်")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        delete_btn = st.button("🗑️ ဖျက်မည်")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        csv = md.convert_df_to_csv(df.drop(columns=["ရွေးပါ", "_id"]))
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        st.download_button(label="📄 CSV", data=csv, file_name='data.csv', mime='text/csv')
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        excel = md.convert_df_to_excel(df.drop(columns=["ရွေးပါ", "_id"]))
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        st.download_button(label="📘 Excel", data=excel, file_name='data.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    if edit_btn:
        md.delete_session()
        selected_rows = df.loc[edited_df["ရွေးပါ"], :]
        if len(selected_rows) == 1:
            st.session_state.selected_id = selected_rows.iloc[0]["_id"]
            st.switch_page("pages/edit.py")
        else:
            st.warning("⚠️ တစ်ခုတည်းကိုသာရွေးပါ။")

    if delete_btn:
        selected_ids = df.loc[edited_df["ရွေးပါ"], "_id"].tolist()
        selected_img_paths = df.loc[edited_df["ရွေးပါ"], "img_path"].tolist()

        if selected_ids:
            # ဓာတ်ပုံဖိုင်တွေကိုဖျက်
            for img_path in selected_img_paths:
                if img_path is None or img_path == "":
                    continue  # img_path မရှိရင် skip လုပ်
                img_path = str(img_path)
                full_path = os.path.join(os.getcwd(), img_path)
                
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        st.error(f"⚠️ ဓာတ်ပုံဖျက်ရာတွင် အမှားဖြစ်ပွားခဲ့ပါသည်: {e}")
            
            # MongoDB က document တွေကိုဖျက်
            collection.delete_many({"_id": {"$in": selected_ids}})
            
            st.success(f"✅ {len(selected_ids)} ကြိမ်ဖျက်ပြီးပြီ။")
            st.rerun()
        else:
            st.warning("⚠️ ဖျက်မယ့်ဒေတာကိုရွေးပါ။")

else:
    st.info("⚠️ အချက်အလက်မရှိပါ။")


        
        

        

    