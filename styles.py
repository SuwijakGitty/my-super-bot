import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Import Google Font (Kanit) */
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Kanit', sans-serif;
        }

        /* =========================================
           🔥 1. SIDEBAR FIX (แก้ให้มองเห็นชัดๆ) 
           ========================================= */
        
        /* พื้นหลัง Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important; /* สีเทาอ่อนๆ สบายตา */
            border-right: 1px solid #e0e0e0;
        }

        /* ตัวหนังสือใน Sidebar ต้องสีเข้มเสมอ! */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #262730 !important; /* สีดำเทาเข้ม */
        }

        /* ปุ่มใน Sidebar (New Chat, Voice Mode) */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background-color: #ffffff !important;
            color: #31333F !important;
            border: 1px solid #d0d0d0 !important;
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            transition: all 0.2s;
        }

        /* ตอนเอาเมาส์ชี้ปุ่ม */
        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: #ff4b4b !important;
            color: #ff4b4b !important;
            background-color: #fff5f5 !important;
        }

        /* =========================================
           ✨ 2. VOICE MODE ANIMATION
           ========================================= */
        .voice-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 0;
        }
        
        .voice-orb {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            box-shadow: 0 0 30px rgba(118, 75, 162, 0.6);
            animation: pulse 2s infinite;
            margin-bottom: 20px;
        }
        
        .voice-status {
            font-size: 1.2rem;
            color: #555;
            font-weight: 500;
            animation: fadeIn 1s ease-in;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(118, 75, 162, 0.7); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(118, 75, 162, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(118, 75, 162, 0); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* =========================================
           📱 3. OTHER UI IMPROVEMENTS
           ========================================= */
        
        /* ซ่อน Header รกๆ ด้านบน */
        header[data-testid="stHeader"] {
            background-color: transparent;
        }

        /* ปรับช่องพิมพ์ข้อความด้านล่าง */
        [data-testid="stChatInput"] {
            border-radius: 20px !important;
        }
        
        /* กรอบข้อความแจ้งเตือน (Toast) */
        div[data-testid="stToast"] {
            background-color: #333 !important;
            color: white !important;
            border-radius: 10px;
        }
        
        /* ข้อความ Disclaimer ตัวเล็กๆ */
        .disclaimer-text {
            font-size: 0.7rem;
            color: #aaa;
            text-align: center;
            margin-top: 20px;
        }

        </style>
    """, unsafe_allow_html=True)