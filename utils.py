import base64
import pandas as pd
from gtts import gTTS
import io
from groq import Groq
import docx
import pdfplumber
from youtube_transcript_api import YouTubeTranscriptApi
from duckduckgo_search import DDGS
import re
import yt_dlp
import os

# --- 1. เครื่องมือจัดการไฟล์ ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        elif "docx" in uploaded_file.name or "word" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            try: return uploaded_file.getvalue().decode("utf-8")
            except: return uploaded_file.getvalue().decode("tis-620")
    except Exception as e: return f"อ่านไฟล์ไม่ได้ครับ: {e}"

# --- 2. ฟังก์ชัน "หูทิพย์" ---
def transcribe_audio(audio_bytes, api_key):
    try:
        client = Groq(api_key=api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3",
            language="th",
            response_format="text"
        )
        return transcription
    except: return None

# --- 3. ฟังก์ชัน "ปากแจ๋ว" ---
def text_to_speech(text, lang='th'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except: return None

# --- 4. 🔥 ฟังก์ชันดูดคลิป (อัปเกรด: อ่านชื่อช่องก่อน!) ---
def get_youtube_content(url, api_key):
    metadata_text = ""
    
    # 0. 🔥 ดึงข้อมูล Metadata (ชื่อช่อง, ชื่อคลิป) ก่อนเลย
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False) # ดึงข้อมูลเฉยๆ ไม่โหลด
            video_title = info.get('title', 'ไม่ระบุชื่อคลิป')
            channel_name = info.get('uploader', 'ไม่ระบุชื่อช่อง')
            view_count = info.get('view_count', 0)
            metadata_text = f"📌 ข้อมูลคลิป:\n- ชื่อคลิป: {video_title}\n- เจ้าของช่อง: {channel_name}\n- ยอดวิว: {view_count:,}\n\n"
    except Exception as e:
        print(f"ดึง Metadata ไม่ได้: {e}")

    # 1. ลองหาซับไตเติ้ล
    try:
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id:
            transcript = YouTubeTranscriptApi.get_transcript(video_id.group(1), languages=['th', 'en'])
            text = " ".join([t['text'] for t in transcript])
            return f"{metadata_text}📜 (แกะจากซับไตเติ้ล):\n{text[:15000]}"
    except:
        pass 

    # 2. ถ้าไม่มีซับ -> ใช้หูฟังแกะเสียง (FFmpeg)
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],
            'ffmpeg_location': '.', 
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists('temp_audio.mp3'):
            client = Groq(api_key=api_key)
            with open('temp_audio.mp3', 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=('temp_audio.mp3', audio_file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            os.remove('temp_audio.mp3')
            return f"{metadata_text}🎧 (แกะจากเสียงในคลิป):\n{transcription}"
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"
    
    return None

# --- 5. ฟังก์ชันค้นหา ---
def search_web(query):
    try:
        results = DDGS().text(query, region='wt-wt', safesearch='off', max_results=3)
        results_list = list(results)
        if not results_list: return "ไม่พบข้อมูลครับ"
        
        summary = ""
        for res in results_list:
            summary += f"- {res['title']}: {res['body']}\n"
        return summary
    except Exception as e:
        return f"ค้นหาไม่ได้ชั่วคราว: {e}"