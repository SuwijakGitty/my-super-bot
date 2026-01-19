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
        
        /* --- Sidebar --- */
        [data-testid="stSidebar"] {
            background-color: #f0f4f9;
            border-right: none;
        }
        
        /* 🔥 แต่งปุ่ม History ใน Sidebar ให้เป็น Card มีกรอบ */
        [data-testid="stSidebar"] button {
            background-color: #ffffff !important;
            border: 1px solid #e0e3e7 !important;
            border-radius: 12px !important;
            padding: 10px 15px !important;
            margin-bottom: 8px !important;
            color: #444746 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            transition: all 0.2s;
            text-align: left !important;
        }
        
        /* ตอนเอาเมาส์ชี้ */
        [data-testid="stSidebar"] button:hover {
            border-color: #0b57d0 !important;
            background-color: #e8f0fe !important;
            color: #0b57d0 !important;
            transform: translateX(3px); /* ขยับขวานิดนึงให้ดูมีลูกเล่น */
        }
        
        /* ปุ่ม New Chat (ปุ่มบนสุด) ให้เด่นหน่อย */
        [data-testid="stSidebar"] button:first-child {
            background-color: #d3e3fd !important; /* สีฟ้าอ่อน */
            border: none !important;
            color: #041e49 !important;
            font-weight: 600 !important;
            text-align: center !important;
        }

        /* --- Chat Bubble --- */
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
        
        /* --- ปุ่มแนบไฟล์ --- */
        .stPopover {
            position: fixed; bottom: 80px; right: 40px; z-index: 999999;
            width: auto !important; height: auto !important; display: inline-block !important;
        }
        .stPopover button {
            background-color: #ffffff !important; color: #444746 !important;
            border: 1px solid #e0e3e7 !important; border-radius: 50% !important;
            width: 50px !important; height: 50px !important; font-size: 24px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .stPopover button:hover {
            background-color: #f0f4f9 !important; color: #0b57d0 !important;
            transform: scale(1.05); box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* --- Input Bar --- */
        .stChatInputContainer textarea {
            border-radius: 24px !important; border: 1px solid #e0e3e7 !important;
            padding-right: 60px !important; padding-top: 15px !important;
            background-color: #f0f4f9 !important; color: #1f1f1f !important;
        }
        .stChatInputContainer textarea:focus {
            background-color: #ffffff !important; border-color: #0b57d0 !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
        }
        
        .disclaimer-text {
            text-align: center; font-size: 12px; color: #444746;
            margin-top: 10px; margin-bottom: 50px;
        }
    </style>
    """, unsafe_allow_html=True)