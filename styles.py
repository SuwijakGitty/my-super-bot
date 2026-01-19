import streamlit as st

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans Thai', sans-serif;
            color: #1f1f1f;
        }
        
        .stApp { background-color: #ffffff; }
        .stDeployButton, [data-testid="stDecoration"], footer { display:none; }
        [data-testid="stSidebar"] { background-color: #f0f4f9; border-right: none; }
        
        /* ปุ่ม Sidebar */
        [data-testid="stSidebar"] button {
            background-color: #ffffff !important;
            border: 1px solid #e0e3e7 !important;
            border-radius: 12px !important;
            padding: 10px 15px !important;
            text-align: left !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
        [data-testid="stSidebar"] button:hover {
            border-color: #0b57d0 !important;
            background-color: #e8f0fe !important;
        }

        /* Chat Bubble */
        .stChatMessage { background-color: transparent; border: none; }
        div[data-testid="stChatMessage"]:nth-child(odd) {
            background-color: #f0f4f9; border-radius: 24px;
            padding: 15px 25px; margin-bottom: 20px; color: #1f1f1f;
            line-height: 1.6; max-width: 85%; margin-left: auto;
        }
        div[data-testid="stChatMessage"]:nth-child(even) {
            background-color: transparent; padding: 0px; margin-bottom: 20px;
            line-height: 1.7; color: #1f1f1f;
        }

        /* 🔥 จัดระเบียบ INPUT BAR (แบบคลีนๆ) */
        
        /* 1. ขยายช่องพิมพ์ให้หลบปุ่มแนบไฟล์ */
        .stChatInputContainer textarea {
            border-radius: 24px !important; 
            border: 1px solid #e0e3e7 !important;
            padding-right: 60px !important; /* เว้นที่ขวา */
            padding-top: 15px !important;
            background-color: #f0f4f9 !important; 
            color: #1f1f1f !important;
        }

        /* 2. ปุ่มแนบไฟล์ (Clip) -> วางมุมขวาล่างของจอ (Fixed) */
        /* การใช้ Fixed Position ชัวร์สุดครับ ไม่ดิ้นตาม text */
        .stPopover {
            position: fixed; 
            bottom: 28px !important; 
            right: 80px !important; /* วางข้างๆ ปุ่มส่ง */
            z-index: 999999;
            width: auto !important; height: auto !important;
        }
        .stPopover button {
            background-color: transparent !important;
            color: #444746 !important;
            border: none !important; 
            width: 35px !important; height: 35px !important; 
            font-size: 20px !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        .stPopover button:hover {
            background-color: #e0e3e7 !important;
            color: #0b57d0 !important;
            border-radius: 50% !important;
        }

        /* Voice Mode Styles */
        .voice-container {
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; height: 60vh;
        }
        .voice-orb {
            width: 150px; height: 150px; border-radius: 50%;
            background: linear-gradient(135deg, #4285f4, #0b57d0);
            box-shadow: 0 0 40px rgba(66, 133, 244, 0.6);
            animation: pulse 3s infinite ease-in-out; margin-bottom: 30px;
        }
        @keyframes pulse {
            0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); }
        }
        .voice-status { font-size: 1.5rem; color: #444746; font-weight: 500; }
        .disclaimer-text { text-align: center; font-size: 12px; color: #444746; margin-top: 10px; margin-bottom: 50px; }

    </style>
    """, unsafe_allow_html=True)