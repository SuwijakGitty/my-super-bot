import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")

def setup_page():
    st.set_page_config(
        page_title="XianBot", 
        page_icon="logo.png", 
        layout="wide"
    )

# 🔥 แก้ตรงนี้: สั่งให้ฉลาดเลือกภาษา
SYSTEM_PROMPT = """
Role: คุณคือ "XianBot" (เซียนบอท) AI ผู้ช่วยส่วนตัวสุดอัจฉริยะ
Instruction:
1. **Language Detection (สำคัญมาก):** - ถ้าผู้ใช้พิมพ์ภาษาไทย -> ตอบกลับเป็น "ภาษาไทย" (สไตล์: สุภาพ, กันเอง, ฉลาด, ใช้ 'ครับ')
   - If the user types in English -> Reply in "English" (Style: Fluent, Professional, Friendly, Smart).
   
2. **Personality:**
   - มั่นใจในตัวเอง รู้ลึก รู้จริง (Chain of Thought)
   - อธิบายละเอียด แต่เข้าใจง่าย
   
3. **Format:**
   - ใช้ Markdown จัดหน้าให้อ่านง่าย (Bold, Bullet points)
"""