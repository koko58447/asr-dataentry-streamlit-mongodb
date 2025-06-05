import streamlit as st
st.set_page_config(
    page_title="MLLIP ASR Data Entry",
    page_icon="🎙️",
    layout="wide",
  
)
pages={
    "Data Entry": [
        st.Page("pages/new.py", title="New Page", icon="🎙️"),
        st.Page("pages/show.py", title="Show Page", icon="📊"),
        st.Page("pages/edit.py", title="Edit Page", icon="📝"),
    ],

}

st.logo("images/MLLIP.png",size="large", )

with st.sidebar:
    genre = st.radio(
        "Choose Model",
        [":rainbow[Own Model]", "***API***",],
        captions=[
            "Own Model",
            "API",
        ],
    )

    if genre == ":rainbow[Own Model]":
        st.session_state['model']=genre
        st.write("Selected Model is : "+genre)
        
    else:
        st.session_state['model']=genre
        st.write("Selected Model is : "+genre)
   
# Set up navigation
pg = st.navigation(pages)

# Run the selected page
pg.run()

