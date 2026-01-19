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
        [data-testid="stSidebar"] { background-color: #f0f4f9; border-right: none; }
        
        /* ปุ่ม History ใน Sidebar */
        [data-testid="stSidebar"] button {
            background-color: #ffffff !important;
            border: 1px solid #e0e3e7 !important;
            border-radius: 12px !important;
            padding: 10px 15px !important;
            margin-bottom: 8px !important;
            color: #444746 !important;
            text-align: left !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
        [data-testid="stSidebar"] button:hover {
            border-color: #0b57d0 !important;
            background-color: #e8f0fe !important;
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

        /* --- Input Bar --- */
        .stChatInputContainer textarea {
            border-radius: 24px !important; border: 1px solid #e0e3e7 !important;
            padding-right: 60px !important; padding-top: 15px !important;
            background-color: #f0f4f9 !important; color: #1f1f1f !important;
        }
        
        /* --- 🔥 Voice Mode ORB (ลูกแก้ว ChatGPT) --- */
        .voice-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 60vh; /* ความสูงเกือบเต็มจอ */
        }
        
        .voice-orb {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4285f4, #0b57d0);
            box-shadow: 0 0 40px rgba(66, 133, 244, 0.6);
            animation: pulse 3s infinite ease-in-out;
            margin-bottom: 30px;
        }
        
        /* แอนิเมชันหายใจวูบวาบ */
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(66, 133, 244, 0.4); }
            50% { transform: scale(1.1); box-shadow: 0 0 60px rgba(66, 133, 244, 0.8); }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(66, 133, 244, 0.4); }
        }
        
        .voice-status {
            font-size: 1.5rem;
            color: #444746;
            font-weight: 500;
            margin-bottom: 20px;
        }

        /* ซ่อน Elements เวลายุใน Voice Mode */
        .stChatInputContainer {
            /* เราจะซ่อน input ปกติเวลาอยู่ใน Voice Mode ด้วย Python logic */
        }

    </style>
    """, unsafe_allow_html=True)