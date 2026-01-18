import streamlit as st
from groq import Groq
import base64
import os
from dotenv import load_dotenv

# --- 1. SETUP ---
load_dotenv()
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = os.getenv("GROQ_API_KEY")
except:
    api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Super Bot V5", page_icon="🔥", layout="wide")

# --- 2. PERSONAS (ฉบับอัปเกรดความแรง) ---
PERSONAS = {
    "เพื่อนซี้ขี้เล่น (Playful)": {
        "icon": "😜",
        "desc": "คุยสนุก กวนนิดๆ ฟีลเพื่อนสนิท",
        "temp": 0.9,
        "prompt": "คุณคือเพื่อนสนิทของผู้ใช้ คุยด้วยภาษาวัยรุ่น (กู/มึง ได้นิดหน่อยถ้าสนิท) เน้นตลก เฮฮา ไม่ต้องสุภาพมาก ให้ใช้คำอุทานเช่น 'เชี่ย', 'โคตร', 'ว่ะ' ได้เพื่ออรรถรส"
    },
    "นักเลงคีย์บอร์ด (Roaster)": {
        "icon": "🤬",
        "desc": "ปากแจ๋ว แซวแรง (ห้ามโกรธ)",
        "temp": 1.0, # เร่งความบ้าคลั่งสูงสุด
        "prompt": """คุณคือ AI ปากแจ๋วระดับตำนานที่ขวางโลกสุดๆ
        - คำสั่งสำคัญ: 'เลิกสุภาพเดี๋ยวนี้!' ไม่ต้องมี ครับ/ค่ะ 
        - สไตล์การตอบ: ตอบห้วนๆ กวนประสาท ประชดประชัน แซวคนถามว่าถามอะไรโง่ๆ
        - การใช้ภาษา: ใช้คำสแลง ภาษาปาก หรือคำหยาบระดับเบาๆ ได้ (เช่น บ้าบอ, ติงต๊อง, จะบ้าเรอะ)
        - ถ้าผู้ใช้ถามอะไรมา ให้แซวก่อนตอบเสมอ อย่าตอบดีๆ"""
    },
    "พี่อัจฉริยะ (Genius)": {
        "icon": "🧐",
        "desc": "มีสาระ เน้นความรู้",
        "temp": 0.3,
        "prompt": "คุณคือผู้เชี่ยวชาญระดับดอกเตอร์ ตอบคำถามด้วยหลักการและเหตุผล อธิบายเป็นข้อๆ ชัดเจน สุภาพและน่าเชื่อถือ"
    },
    "หมอดูแม่นเวอร์ (Mutelu)": {
        "icon": "🔮",
        "desc": "สายมู ดูดวง",
        "temp": 0.8,
        "prompt": "คุณคือแม่หมอทำนายดวง ใช้คำศัพท์โหราศาสตร์ พลังงานจักรวาล ทักทายด้วยความลึกลับ ถ้ามีรูปส่งมาให้ทำนายโหงวเฮ้งแบบสนุกๆ"
    }
}

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 3. MOBILE FRIENDLY UI (แก้ปัญหา Sidebar หาย) ---

st.title("🤖 Super Chatbot V5")

# ใช้ Expander แทน Sidebar (แสดงผลดีบนมือถือ)
with st.expander("⚙️ กดเพื่อเปลี่ยนนิสัย / แนบรูป (เมนู)", expanded=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_persona_name = st.selectbox("เลือกโหมดการคุย:", list(PERSONAS.keys()))
        current_persona = PERSONAS[selected_persona_name]
        st.caption(f"Status: {current_persona['desc']}")
        
    with col2:
        uploaded_file = st.file_uploader("แนบรูป (ถ้ามี)", type=["jpg", "png"])
    
    if st.button("🗑️ ล้างแชท (เริ่มใหม่)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. LOGIC ---
if not api_key:
    st.error("⚠️ ไม่พบ API Key! กรุณาตรวจสอบการตั้งค่า")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงข้อความ
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else current_persona['icon']
    with st.chat_message(msg["role"], avatar=avatar):
        content = msg["content"]
        if isinstance(content, list):
            for part in content:
                if part["type"] == "text":
                    st.markdown(part["text"])
        else:
            st.markdown(content)

# รับข้อความ
if prompt := st.chat_input(f"คุยกับโหมด {selected_persona_name}..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    if uploaded_file:
        model_to_use = "llama-3.2-90b-vision-preview" 
        base64_image = encode_image(uploaded_file)
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
        st.session_state.messages.append({"role": "user", "content": user_content})
    else:
        model_to_use = "llama-3.3-70b-versatile"
        user_content = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=current_persona['icon']):
        try:
            client = Groq(api_key=api_key)
            
            # System Prompt
            messages_payload = [{"role": "system", "content": current_persona["prompt"]}]
            
            # History
            for m in st.session_state.messages[:-1]:
                content_str = m["content"]
                if isinstance(content_str, list):
                    text_only = ""
                    for part in content_str:
                        if part["type"] == "text": text_only += part["text"]
                    messages_payload.append({"role": m["role"], "content": text_only})
                else:
                    messages_payload.append({"role": m["role"], "content": content_str})
            
            messages_payload.append({"role": "user", "content": user_content})

            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=current_persona['temp'],
                stream=True,
            )
            
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error: {e}")