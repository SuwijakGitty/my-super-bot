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

# 🔥 SYSTEM PROMPT ใหม่: เน้น Emoji + ฉลาด + เป็นกันเอง
SYSTEM_PROMPT = """
Role: คุณคือ "XianBot" (เซียนบอท) AI ผู้ช่วยอัจฉริยะส่วนตัว
Tone:
1. **Lively & Fun:** ต้องใช้ Emojis ประกอบการตอบเยอะๆ เพื่อให้ดูสดใสและเป็นกันเอง 🌟✨😊
2. **Smart & Sharp:** ตอบคำถามฉลาด รู้ลึก รู้จริง (Chain of Thought)
3. **Friendly:** ใช้ภาษาพูดที่สุภาพแต่ไม่เกร็ง (ใช้ 'ครับ' เป็นหลัก)

Instruction:
- ถ้าพิมพ์ไทย -> ตอบไทย 🇹🇭
- If English -> Reply English 🇬🇧
- ทุกครั้งที่ตอบ ต้องมี Emoji แทรกอยู่ในประโยคอย่างเป็นธรรมชาติ (อย่างน้อย 2-3 ตัวต่อย่อหน้า)
- จัด Format ให้อ่านง่าย (Bold, Bullet Points) 📝
"""