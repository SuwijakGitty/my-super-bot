import streamlit as st
from groq import Groq
import base64
import os
import pandas as pd
import PyPDF2
from dotenv import load_dotenv

# ==========================================
# 1. BRAIN & CONFIG (สมองส่วนหลัก)
# ==========================================
load_dotenv()
try:
    API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
except:
    API_KEY = os.getenv("GROQ_API_KEY")

# 🔥 ฝังนิสัยเดียวที่นี่ (ฉลาด + ตอบยาว + มีคาแรคเตอร์)
SYSTEM_PROMPT = """
Role: คุณคือ AI ผู้ช่วยอัจฉริยะ (Senior Expert & Buddy)
Language: ภาษาไทย (ธรรมชาติ, สุภาพแต่เป็นกันเอง, ห้ามใช้ 'คะ/ค่ะ' ให้ใช้ 'ครับ' หรือไม่มีหางเสียง)

Instruction (คำสั่งสำคัญ):
1. **ตอบให้ละเอียด (Detailed):** ห้ามตอบสั้นๆ ห้วนๆ เด็ดขาด! ต้องอธิบายที่มาที่ไป เหตุผล และยกตัวอย่างประกอบเสมอ
2. **คิดวิเคราะห์ (Chain of Thought):** เวลาเจอคำถามยากๆ ให้แสดงกระบวนการคิด หรือแจกแจงเป็นข้อๆ (Bullet points) เพื่อให้อ่านง่าย
3. **ความเป็นกันเอง (Tone):** ไม่ต้องทางการมาก เหมือนคุยกับรุ่นพี่ที่เก่งมากๆ ปากแจ๋วนิดๆ ได้เพื่อให้ไม่น่าเบื่อ
4. **ถ้าเป็นโค้ด (Coding):** ต้องเขียนโค้ดที่สมบูรณ์ (Best Practice) พร้อมอธิบายการทำงานทีละส่วน
5. **เป้าหมาย:** ทำให้ผู้ใช้รู้สึกว่า "โห... รู้ลึกจังวะ" ทุกครั้งที่ตอบ
"""

st.set_page_config(page_title="Gemini V15", page_icon="🧠", layout="wide")

# ==========================================
# 2. UI STYLE (หน้าตา)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }
    
    footer {visibility: hidden;} .stDeployButton {display:none;}
    .stApp {background-color: #ffffff;}

    /* Chat Bubble */
    .stChatMessage { background-color: transparent; border: none; }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #eff3f8; border-radius: 20px;
        padding: 15px 25px; margin-bottom: 15px; color: #1f1f1f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* เพิ่มเงาให้นูนสวย */
        line-height: 1.6; /* เพิ่มระยะบรรทัดให้อ่านง่ายสำหรับข้อความยาวๆ */
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent; padding: 0px 10px; margin-bottom: 15px;
        line-height: 1.6;
    }

    /* Floating Button (ขวาล่าง) */
    .stPopover {
        position: fixed; bottom: 85px; right: 30px; z-index: 999999;
        width: auto !important; height: auto !important; display: inline-block !important;
    }
    .stPopover button {
        background-color: #f0f4f9 !important; color: #444746 !important;
        border: none !important; border-radius: 50% !important;
        width: 55px !important; height: 55px !important; /* ใหญ่ขึ้นนิดนึง */
        font-size: 24px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stPopover button:hover {
        background-color: #d3e3fd !important; color: #0b57d0 !important; transform: scale(1.1);
    }

    /* Input Box Adjustment */
    .stChatInputContainer textarea { padding-right: 70px !important; }
    div[data-testid="stChatInput"] { padding-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            pdf = PyPDF2.PdfReader(uploaded_file)
            return "".join([p.extract_text() for p in pdf.pages])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except: return "อ่านไฟล์ไม่ได้"

def stream_parser(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# ==========================================
# 4. MAIN APP
# ==========================================
with st.sidebar:
    st.title("🧠 Gemini Ultimate")
    st.caption("Version 15: Deep Thinker")
    if st.button("➕ Clear Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.info("💡 Tip: ถามสั้นๆ ได้ แต่บอทจะตอบยาวและละเอียดครับ")

if "messages" not in st.session_state: st.session_state.messages = []

# Welcome text
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; margin-top: 60px;">
        <h1 style="background: linear-gradient(to right, #0b57d0, #a142f4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            พร้อมใช้งานครับลูกพี่! 🧠
        </h1>
        <p style="color: gray; font-size: 1.1em;">ถามมาได้เลย เดี๋ยวผมวิเคราะห์ให้แบบเจาะลึก!</p>
    </div>
    """, unsafe_allow_html=True)

# Render Chat
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🧠"
    with st.chat_message(role, avatar=avatar):
        if isinstance(msg["content"], list):
            for p in msg["content"]:
                if p["type"]=="text": st.markdown(p["text"])
                if p["type"]=="image_url": st.image(p["image_url"]["url"], width=250)
        else:
            st.markdown(msg["content"])

# File Uploader
with st.popover("📎", help="แนบไฟล์"):
    uploaded_file = st.file_uploader("Upload", label_visibility="collapsed")
    file_txt = extract_file(uploaded_file) if uploaded_file and "image" not in uploaded_file.type else ""

# Input & Logic
if prompt := st.chat_input("พิมพ์คำถามมาเลย..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # Logic
    user_content = prompt
    model = "llama-3.3-70b-versatile"
    
    # ใช้ System Prompt เดียวที่ฝังไว้เลย
    final_instruction = SYSTEM_PROMPT

    if uploaded_file:
        if "image" in uploaded_file.type:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
            img = encode_image(uploaded_file)
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]
        else:
            final_instruction += f"\n\n[ข้อมูลไฟล์แนบ]: {file_txt}\nคำสั่ง: วิเคราะห์ข้อมูลนี้อย่างละเอียดที่สุด"
    
    st.session_state.messages.append({"role": "user", "content": user_content})

    # ส่ง API
    with st.chat_message("assistant", avatar="🧠"):
        try:
            client = Groq(api_key=API_KEY)
            
            messages = [{"role": "system", "content": final_instruction}]
            # ย่อ History เก่าๆ เพื่อประหยัด Token แต่ยังจำได้
            for m in st.session_state.messages[:-1]:
                content = m["content"]
                if isinstance(content, list):
                    content = "".join([x["text"] for x in content if x["type"]=="text"])
                messages.append({"role": m["role"], "content": content})
            messages.append({"role": "user", "content": user_content})

            stream = client.chat.completions.create(
                messages=messages, 
                model=model, 
                temperature=0.7,   # ลดความมั่วลงนิดนึงเพื่อให้ดูฉลาดขึ้น
                max_tokens=6000,   # 🔥 เพิ่มโควต้าให้ตอบได้ยาวเหยียด (สะใจแน่นอน)
                stream=True
            )
            response = st.write_stream(stream_parser(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error: {e}")