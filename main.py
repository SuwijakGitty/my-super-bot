import streamlit as st
from groq import Groq
import base64
import os
import pandas as pd
import PyPDF2
from dotenv import load_dotenv

# --- 1. CONFIG & SETUP ---
load_dotenv()
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = os.getenv("GROQ_API_KEY")
except:
    api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI Pro Chat", page_icon="💬", layout="wide")

# --- 2. MODERN UI STYLING (CSS MAGIC) ---
st.markdown("""
<style>
    /* พื้นหลังและฟอนต์ */
    .stApp {
        background: linear-gradient(to right, #1a1a1a, #2d2d2d);
        color: #ffffff;
    }
    
    /* ปรับแต่ง Chat Bubble ให้เหมือนแอปแชทจริง */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Avatar ให้ดูดี */
    .stChatMessage .stChatMessageAvatar {
        background-color: #4CAF50;
        color: white;
    }

    /* ปุ่มกดต่างๆ ให้ดูโค้งมน */
    .stButton>button {
        border-radius: 20px;
        border: none;
        background-color: #4CAF50;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* ซ่อน Header รกๆ */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* จัดการ File Uploader ให้สวย */
    [data-testid="stFileUploader"] {
        padding: 10px;
        border: 1px dashed #4CAF50;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_text_from_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- 4. SIDEBAR (เมนูหลัก) ---
with st.sidebar:
    st.title("🤖 AI Controller")
    st.caption("Select Personality")
    
    mode = st.selectbox("โหมดการทำงาน", [
        "🧠 ผู้ช่วยอัจฉริยะ (Smart)",
        "💻 โปรแกรมเมอร์ (Coder)",
        "📝 นักสรุปงาน (Summarizer)",
        "🤬 เพื่อนปากแจ๋ว (Roaster)"
    ])
    
    st.markdown("---")
    
    # ปุ่มล้างแชทแบบสวยๆ
    col_reset, col_link = st.columns(2)
    with col_reset:
        if st.button("🗑️ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.file_content = None # ล้างไฟล์ด้วย
            st.rerun()
    with col_link:
        st.link_button("📂 Repo", "https://github.com/", use_container_width=True)

# --- 5. MAIN CHAT AREA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title Area
st.subheader(f"{mode}")

# --- พื้นที่แนบไฟล์ (ย้ายมาไว้ตรงกลาง หน้าตาเหมือนปุ่มเครื่องมือ) ---
# ใช้ Expander หรือ Popover เพื่อไม่ให้รก
with st.popover("📎 กดเพื่อแนบไฟล์ / รูปภาพ (Attach)", use_container_width=True):
    st.markdown("##### 📂 แนบเอกสาร หรือ รูปภาพที่นี่")
    uploaded_file = st.file_uploader(
        "รองรับ: PDF, Excel, CSV, รูปภาพ", 
        type=["pdf", "csv", "xlsx", "txt", "jpg", "png"],
        label_visibility="collapsed"
    )
    
    # Preview
    file_content = ""
    is_image = False
    
    if uploaded_file:
        st.success(f"✅ แนบไฟล์: {uploaded_file.name}")
        file_type = uploaded_file.type
        if "image" in file_type:
            is_image = True
            st.image(uploaded_file, caption="Preview", width=200)
        else:
            is_image = False
            # อ่านไฟล์เงียบๆ
            if uploaded_file:
                file_content = extract_text_from_file(uploaded_file)

# Display Chat History
for msg in st.session_state.messages:
    # แยกฝั่ง: User ขวา / Bot ซ้าย (ใช้ Columns ช่วยจัด)
    if msg["role"] == "user":
        # User Message Styling
        with st.chat_message("user", avatar="👤"):
            content = msg["content"]
            if isinstance(content, list):
                for part in content:
                    if part["type"] == "text": st.markdown(part["text"])
                    if part["type"] == "image_url": st.markdown("*(ส่งรูปภาพ)*")
            else:
                st.markdown(content)
    else:
        # Bot Message Styling
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])

# --- 6. CHAT INPUT (อยู่ล่างสุด) ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # 1. แสดงข้อความ User
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # 2. เตรียม Context
    system_prompts = {
        "🧠 ผู้ช่วยอัจฉริยะ (Smart)": "คุณคือผู้ช่วย AI ที่ฉลาดและสุภาพ",
        "💻 โปรแกรมเมอร์ (Coder)": "คุณคือ Senior Developer ตอบด้วยโค้ด",
        "📝 นักสรุปงาน (Summarizer)": "สรุปข้อมูลเป็นข้อๆ ชัดเจน",
        "🤬 เพื่อนปากแจ๋ว (Roaster)": "คุณคือเพื่อนปากแจ๋ว เน้นตลก กวนประสาท (ไม่ต้องสุภาพ)"
    }
    
    final_prompt = system_prompts[mode]
    # ถ้ามีไฟล์แนบ ให้ยัดเนื้อหาไฟล์เข้าไปใน System Prompt
    if file_content:
        final_prompt += f"\n\n[FILE CONTEXT]:\n{file_content}\n\n[INSTRUCTION]: ตอบโดยอ้างอิงข้อมูลในไฟล์นี้"

    messages_payload = [{"role": "system", "content": final_prompt}]

    # 3. จัดการรูปภาพ/ข้อความ
    user_msg_obj = prompt
    model_to_use = "llama-3.3-70b-versatile" # Default Text Model

    if is_image and uploaded_file:
        model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct" # Vision Model
        base64_img = encode_image(uploaded_file)
        user_msg_obj = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
        ]
        st.session_state.messages.append({"role": "user", "content": user_msg_obj})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 4. รวม History
    for m in st.session_state.messages[:-1]:
        # Clean history object
        c = m["content"]
        if isinstance(c, list): # ถ้าประวัติเก่ามีรูป ให้เอาแต่ text ไป
            text_only = ""
            for p in c:
                if p["type"] == "text": text_only += p["text"]
            messages_payload.append({"role": m["role"], "content": text_only})
        else:
            messages_payload.append({"role": m["role"], "content": c})
    
    messages_payload.append({"role": "user", "content": user_msg_obj})

    # 5. ส่งให้ AI
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=0.7,
                stream=True,
            )
            
            def parse_stream(stream):
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            response = st.write_stream(parse_stream(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error: {e}")