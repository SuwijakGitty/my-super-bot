import streamlit as st
import os
from dotenv import load_dotenv

# โหลดตัวแปร
load_dotenv()

def setup_page():
    st.set_page_config(
        page_title="XianBot God Mode",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # ซ่อนเมนูรกๆ
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def get_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("ไม่พบ GROQ_API_KEY ในไฟล์ .env")
        st.stop()
    return api_key