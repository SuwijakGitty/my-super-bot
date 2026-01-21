import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Import Google Font: Inter (เหมือน Gemini/ChatGPT) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap'); /* สำรองสำหรับภาษาไทย */

        html, body, [class*="css"] {
            font-family: 'Inter', 'Sarabun', sans-serif !important;
        }

        /* =========================================
           ✨ GEMINI THEME
           ========================================= */
        
        /* Sidebar: สีเทาอ่อน สะอาดตา */
        [data-testid="stSidebar"] {
            background-color: #f0f4f9 !important;
            border-right: none;
        }
        
        /* ปุ่มใน Sidebar: โค้งมน ลอยๆ */
        [data-testid="stSidebar"] .stButton > button {
            background-color: #dde3ea !important;
            color: #444746 !important;
            border: none !important;
            border-radius: 24px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.2s;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #c4c7c5 !important;
            color: #1f1f1f !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Chat Input: โค้งมนเหมือนแคปซูลยา */
        [data-testid="stChatInput"] {
            background-color: #f0f4f9 !important;
            border-radius: 30px !important;
            border: 1px solid #e0e0e0;
        }
        
        /* กล่องข้อความ User (สีเทาเข้ม ปรับให้มน) */
        div[data-testid="stChatMessage"] {
            background-color: transparent;
            padding: 1rem;
        }
        div[data-testid="stChatMessage"][data-testid="user"] {
            background-color: #f0f4f9; /* เทาอ่อนแบบ Gemini */
            border-radius: 20px;
        }

        /* Avatar */
        div[data-testid="stChatMessage"] .st-emotion-cache-1p1m4t5 {
            background-color: #f0f4f9;
        }

        /* =========================================
           🚀 VOICE ANIMATION
           ========================================= */
        .voice-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0;
        }
        .voice-orb {
            width: 100px; height: 100px;
            background: linear-gradient(135deg, #4285f4 0%, #d96570 100%);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0.7); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(66, 133, 244, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0); }
        }
        </style>
    """, unsafe_allow_html=True)