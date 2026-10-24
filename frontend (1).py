import os
import math
import sqlite3
import html
from datetime import datetime
from io import BytesIO

import requests
import streamlit as st
from gtts import gTTS
from streamlit_geolocation import streamlit_geolocation
from streamlit_mic_recorder import speech_to_text

# -------------------- Configuration --------------------
APP_TITLE = "WorkSortage"
DB_PATH = "/content/worksortage.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"

st.set_page_config(page_title=APP_TITLE, page_icon="🧰", layout="wide")

LANGUAGES = {
    "English": {"stt": "en-US", "tts": "en", "instruction": "Reply in simple English."},
    "తెలుగు": {"stt": "te-IN", "tts": "te", "instruction": "సులభమైన తెలుగులో సమాధానం ఇవ్వండి."},
    "हिन्दी": {"stt": "hi-IN", "tts": "hi", "instruction": "सरल हिंदी में जवाब दें।"},
}
CATEGORIES = {
    "🦺 Construction": "Construction",
    "📦 Delivery": "Delivery",
    "🚚 Driving": "Driving",
    "🧹 Cleaning": "Cleaning",
    "🍳 Cooking": "Cooking",
    "🏭 Factory": "Factory",
    "🛍️ Shop / Retail": "Shop / Retail",
    "🛡️ Security": "Security",
    "🖥️ Office": "Office",
    "🧰 Other": "Other",
}
CATEGORY_ICONS = {v: k.split(" ", 1)[0] for k, v in CATEGORIES.items()}

# All built-in interface text is translated when the language selector changes.
# Job titles and descriptions are entered by employers, so they remain in the language supplied by them.
UI_TRANSLATIONS = {
    "తెలుగు": {
        "Your local job companion": "మీ స్థానిక ఉద్యోగ సహాయకుడు", "Navigate": "పేజీలు", "Simple • Local • Worker-friendly": "సులభం • స్థానికం • కార్మికులకు అనుకూలం",
        "Find Jobs": "ఉద్యోగాలను వెతకండి", "Voice Assistant": "వాయిస్ సహాయకుడు", "Post a Job": "ఉద్యోగాన్ని పోస్ట్ చేయండి", "My Applications": "నా దరఖాస్తులు",
        "Find nearby work. Contact employers. Apply with confidence.": "దగ్గరలోని పనిని కనుగొనండి. యజమానులను సంప్రదించండి. నమ్మకంగా దరఖాస్తు చేయండి.",
        "Find jobs near you": "మీ దగ్గర ఉద్యోగాలను కనుగొనండి", "Search jobs": "ఉద్యోగాలను వెతకండి", "Helper, delivery, cleaner...": "సహాయకుడు, డెలివరీ, క్లీనర్...", "Job field": "పని రంగం", "All categories": "అన్ని రంగాలు",
        "Current location and distance": "ప్రస్తుత స్థానం మరియు దూరం", "Click the location control and allow location permission in your browser.": "స్థాన బటన్‌ను నొక్కి, బ్రౌజర్‌లో లొకేషన్ అనుమతించండి.", "Current location received.": "ప్రస్తుత స్థానం పొందబడింది.", "Maximum distance (km)": "గరిష్ఠ దూరం (కి.మీ.)", "Or enter a town / area": "లేదా పట్టణం / ప్రాంతం నమోదు చేయండి", "Example: Kakinada": "ఉదాహరణ: కాకినాడ", "Find this area": "ఈ ప్రాంతాన్ని కనుగొనండి", "Looking up area...": "ప్రాంతాన్ని వెతుకుతున్నాం...", "Area not found. Try a more specific place.": "ప్రాంతం కనబడలేదు. మరింత స్పష్టమైన ప్రదేశాన్ని నమోదు చేయండి.", "Area location set.": "ప్రాంత స్థానం సెట్ అయింది.",
        "No matching jobs found. Try a different search or post a job.": "సరిపోయే ఉద్యోగాలు లేవు. మరోసారి వెతకండి లేదా ఉద్యోగాన్ని పోస్ట్ చేయండి.", "Pay": "వేతనం", "Employer": "యజమాని", "Call employer": "యజమానికి కాల్ చేయండి", "Email employer": "యజమానికి ఇమెయిల్ చేయండి", "No contact details provided.": "సంప్రదింపు వివరాలు ఇవ్వలేదు.", "Apply for this job": "ఈ ఉద్యోగానికి దరఖాస్తు చేయండి", "Your name": "మీ పేరు", "Your phone number": "మీ ఫోన్ నంబర్", "Message (optional)": "సందేశం (ఐచ్ఛికం)", "Submit application": "దరఖాస్తు సమర్పించండి", "Please enter your name and phone number.": "మీ పేరు మరియు ఫోన్ నంబర్ నమోదు చేయండి.", "Application saved in this demo. Please also contact the employer directly.": "దరఖాస్తు సేవ్ అయింది. యజమానిని నేరుగా కూడా సంప్రదించండి.",
        "Speak or type a question. Choose Telugu or Hindi from the language menu.": "ప్రశ్నను మాట్లాడండి లేదా టైప్ చేయండి. భాషా మెనూలో తెలుగు లేదా హిందీ ఎంచుకోండి.", "Your question": "మీ ప్రశ్న", "Ask about jobs or using WorkSortage...": "ఉద్యోగాలు లేదా WorkSortage గురించి అడగండి...", "Ask Gemma AI": "Gemma AIని అడగండి", "Clear conversation": "సంభాషణను తొలగించండి", "Please speak or type a question.": "దయచేసి ప్రశ్నను మాట్లాడండి లేదా టైప్ చేయండి.", "Gemma is thinking...": "Gemma ఆలోచిస్తోంది...", "Cannot reach Ollama. Check that Ollama is running and Gemma is installed.": "Ollamaను చేరలేకపోయాం. Ollama నడుస్తోందో, Gemma ఇన్‌స్టాల్ అయిందో చూడండి.", "Speak latest answer": "తాజా సమాధానాన్ని వినండి", "Preparing audio...": "ఆడియో సిద్ధం చేస్తున్నాం...", "Text-to-speech failed: ": "స్పీచ్ ఆడియో తయారు కాలేదు: ",
        "Employers can add local work opportunities.": "యజమానులు స్థానిక ఉద్యోగ అవకాశాలను జోడించవచ్చు.", "Job title *": "ఉద్యోగ పేరు *", "Work area / town *": "పని ప్రాంతం / పట్టణం *", "Salary or daily pay *": "జీతం లేదా రోజువారీ వేతనం *", "Employer name *": "యజమాని పేరు *", "Contact phone": "సంప్రదింపు ఫోన్", "Contact email": "సంప్రదింపు ఇమెయిల్", "Job details *": "ఉద్యోగ వివరాలు *", "Coordinates are optional, but required for exact distance calculations.": "స్థాన కోఆర్డినేట్లు ఐచ్ఛికం; ఖచ్చితమైన దూరం లెక్కించడానికి అవసరం.", "Job latitude (optional)": "ఉద్యోగ అక్షాంశం (ఐచ్ఛికం)", "Job longitude (optional)": "ఉద్యోగ రేఖాంశం (ఐచ్ఛికం)", "Publish job": "ఉద్యోగాన్ని ప్రచురించండి", "Please complete all required fields.": "అవసరమైన అన్ని వివరాలు పూరించండి.", "Enter both coordinates or leave both blank.": "రెండు కోఆర్డినేట్లను నమోదు చేయండి లేదా రెండింటినీ ఖాళీగా ఉంచండి.", "Coordinates are outside the valid range.": "కోఆర్డినేట్లు సరైన పరిధిలో లేవు.", "Job published successfully!": "ఉద్యోగం విజయవంతంగా ప్రచురించబడింది!", "Latitude and longitude must be valid numbers.": "అక్షాంశం, రేఖాంశం సరైన సంఖ్యలుగా ఉండాలి.",
        "You have not applied for any jobs yet.": "మీరు ఇంకా ఏ ఉద్యోగానికీ దరఖాస్తు చేయలేదు.", "Job no longer available": "ఉద్యోగం ఇప్పుడు అందుబాటులో లేదు", "Unknown area": "తెలియని ప్రాంతం", "Unknown employer": "తెలియని యజమాని", "Name:": "పేరు:", "Phone:": "ఫోన్:", "Message:": "సందేశం:", "Submitted:": "సమర్పించిన సమయం:", "Listings and applications are saved in this Colab runtime.": "ఉద్యోగాలు, దరఖాస్తులు ఈ Colab రన్‌టైమ్‌లో సేవ్ అవుతాయి.", T("This version is not yet connected to your friend's FastAPI backend."): "ఈ వెర్షన్ ఇంకా మీ స్నేహితుడి FastAPI బ్యాక్‌ఎండ్‌కు కనెక్ట్ కాలేదు.",
        "Construction": "నిర్మాణం", "Delivery": "డెలివరీ", "Driving": "డ్రైవింగ్", "Cleaning": "శుభ్రపరచడం", "Cooking": "వంట", "Factory": "ఫ్యాక్టరీ", "Shop / Retail": "దుకాణం / రిటైల్", "Security": "భద్రత", "Office": "ఆఫీస్", "Other": "ఇతర"
    },
    "हिन्दी": {
        "Your local job companion": "आपका स्थानीय नौकरी सहायक", "Navigate": "मेन्यू", "Simple • Local • Worker-friendly": "आसान • स्थानीय • श्रमिकों के लिए", "Find Jobs": "नौकरियाँ खोजें", "Voice Assistant": "वॉइस सहायक", "Post a Job": "नौकरी पोस्ट करें", "My Applications": "मेरे आवेदन",
        "Find nearby work. Contact employers. Apply with confidence.": "पास में काम खोजें। नियोक्ताओं से संपर्क करें। आत्मविश्वास से आवेदन करें।", "Find jobs near you": "अपने पास नौकरियाँ खोजें", "Search jobs": "नौकरियाँ खोजें", "Helper, delivery, cleaner...": "हेल्पर, डिलीवरी, सफाई कर्मचारी...", "Job field": "काम का क्षेत्र", "All categories": "सभी श्रेणियाँ", "Current location and distance": "वर्तमान स्थान और दूरी", "Click the location control and allow location permission in your browser.": "लोकेशन बटन दबाएँ और ब्राउज़र में अनुमति दें।", "Current location received.": "वर्तमान स्थान मिल गया।", "Maximum distance (km)": "अधिकतम दूरी (किमी)", "Or enter a town / area": "या शहर / क्षेत्र दर्ज करें", "Example: Kakinada": "उदाहरण: काकीनाडा", "Find this area": "यह क्षेत्र खोजें", "Looking up area...": "क्षेत्र खोजा जा रहा है...", "Area not found. Try a more specific place.": "क्षेत्र नहीं मिला। अधिक स्पष्ट स्थान लिखें।", "Area location set.": "क्षेत्र का स्थान सेट हो गया।", "No matching jobs found. Try a different search or post a job.": "कोई मेल खाती नौकरी नहीं मिली। दूसरी खोज करें या नौकरी पोस्ट करें।", "Pay": "वेतन", "Employer": "नियोक्ता", "Call employer": "नियोक्ता को कॉल करें", "Email employer": "नियोक्ता को ईमेल करें", "No contact details provided.": "संपर्क विवरण उपलब्ध नहीं हैं।", "Apply for this job": "इस नौकरी के लिए आवेदन करें", "Your name": "आपका नाम", "Your phone number": "आपका फ़ोन नंबर", "Message (optional)": "संदेश (वैकल्पिक)", "Submit application": "आवेदन जमा करें", "Please enter your name and phone number.": "अपना नाम और फ़ोन नंबर दर्ज करें।", "Application saved in this demo. Please also contact the employer directly.": "आवेदन सेव हो गया। नियोक्ता से सीधे भी संपर्क करें।",
        "Speak or type a question. Choose Telugu or Hindi from the language menu.": "अपना प्रश्न बोलें या टाइप करें। भाषा मेन्यू में तेलुगु या हिंदी चुनें।", "Your question": "आपका प्रश्न", "Ask about jobs or using WorkSortage...": "नौकरी या WorkSortage के बारे में पूछें...", "Ask Gemma AI": "Gemma AI से पूछें", "Clear conversation": "बातचीत साफ़ करें", "Please speak or type a question.": "कृपया प्रश्न बोलें या टाइप करें।", "Gemma is thinking...": "Gemma सोच रहा है...", "Cannot reach Ollama. Check that Ollama is running and Gemma is installed.": "Ollama से कनेक्ट नहीं हो रहा। जाँचें कि Ollama चल रहा है और Gemma इंस्टॉल है।", "Speak latest answer": "नवीनतम उत्तर सुनें", "Preparing audio...": "ऑडियो तैयार हो रहा है...", "Text-to-speech failed: ": "आवाज़ बनाने में विफल: ",
        "Employers can add local work opportunities.": "नियोक्ता स्थानीय काम के अवसर जोड़ सकते हैं।", "Job title *": "नौकरी का नाम *", "Work area / town *": "काम का क्षेत्र / शहर *", "Salary or daily pay *": "वेतन या दैनिक मज़दूरी *", "Employer name *": "नियोक्ता का नाम *", "Contact phone": "संपर्क फ़ोन", "Contact email": "संपर्क ईमेल", "Job details *": "नौकरी का विवरण *", "Coordinates are optional, but required for exact distance calculations.": "स्थान निर्देशांक वैकल्पिक हैं, लेकिन सटीक दूरी के लिए ज़रूरी हैं।", "Job latitude (optional)": "नौकरी का अक्षांश (वैकल्पिक)", "Job longitude (optional)": "नौकरी का देशांतर (वैकल्पिक)", "Publish job": "नौकरी प्रकाशित करें", "Please complete all required fields.": "कृपया सभी ज़रूरी फ़ील्ड भरें।", "Enter both coordinates or leave both blank.": "दोनों निर्देशांक भरें या दोनों खाली छोड़ें।", "Coordinates are outside the valid range.": "निर्देशांक सही सीमा में नहीं हैं।", "Job published successfully!": "नौकरी सफलतापूर्वक प्रकाशित हुई!", "Latitude and longitude must be valid numbers.": "अक्षांश और देशांतर सही संख्या होने चाहिए।", "You have not applied for any jobs yet.": "आपने अभी तक किसी नौकरी के लिए आवेदन नहीं किया है।", "Job no longer available": "नौकरी अब उपलब्ध नहीं है", "Unknown area": "अज्ञात क्षेत्र", "Unknown employer": "अज्ञात नियोक्ता", "Name:": "नाम:", "Phone:": "फ़ोन:", "Message:": "संदेश:", "Submitted:": "जमा किया गया:", "Listings and applications are saved in this Colab runtime.": "नौकरियाँ और आवेदन इस Colab रनटाइम में सेव होते हैं।", T("This version is not yet connected to your friend's FastAPI backend."): "यह संस्करण अभी आपके मित्र के FastAPI बैकएंड से जुड़ा नहीं है।", "Construction": "निर्माण", "Delivery": "डिलीवरी", "Driving": "ड्राइविंग", "Cleaning": "सफाई", "Cooking": "खाना बनाना", "Factory": "फ़ैक्टरी", "Shop / Retail": "दुकान / रिटेल", "Security": "सुरक्षा", "Office": "ऑफ़िस", "Other": "अन्य"
    }
}

def T(text):
    """Translate built-in UI text for the selected language."""
    return UI_TRANSLATIONS.get(st.session_state.get("selected_language", "English"), {}).get(text, text)

CATEGORY_ICONS = {
    "Construction": "👷", "Delivery": "📦", "Driving": "🚚", "Cleaning": "🧹",
    "Cooking": "👨‍🍳", "Factory": "🏭", "Shop / Retail": "🛍️", "Security": "🛡️",
    "Office": "💻", "Other": "🧰"
}

# -------------------- Styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: #fff8f0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #35205c, #5b2c83); }
[data-testid="stSidebar"] * { color: #fff !important; }
.hero {
  background: linear-gradient(120deg, #4b247a, #873fb0, #f59e0b);
  padding: 30px; border-radius: 22px; color: white; margin-bottom: 22px;
  box-shadow: 0 10px 28px rgba(75,36,122,.18);
}
.hero h1 { color: white; margin-bottom: 6px; letter-spacing: -.5px; }
.hero p { color: #fff7ed; font-size: 17px; }
.stButton > button[kind="primary"], .stFormSubmitButton > button { background: #6d3294; border-color: #6d3294; }
[data-testid="stMetric"] { background: white; padding: 14px; border-radius: 14px; border: 1px solid #f1dfcf; }
.small-muted { color: #766783; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# -------------------- SQLite database --------------------
def connect_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL, category TEXT NOT NULL,
          description TEXT NOT NULL, city TEXT NOT NULL, pay TEXT NOT NULL,
          employer TEXT NOT NULL, phone TEXT, email TEXT,
          latitude REAL, longitude REAL, created_at TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          job_id INTEGER NOT NULL, applicant_name TEXT NOT NULL,
          applicant_phone TEXT NOT NULL, note TEXT,
          created_at TEXT NOT NULL
        )""")

def fetch_jobs(category="All categories", search=""):
    sql = "SELECT * FROM jobs"
    clauses, params = [], []
    if category != "All categories":
        clauses.append("category = ?")
        params.append(category)
    if search.strip():
        pattern = "%" + search.strip() + "%"
        clauses.append("(title LIKE ? OR description LIKE ? OR city LIKE ? OR category LIKE ?)")
        params.extend([pattern, pattern, pattern, pattern])
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC"
    with connect_db() as conn:
        return conn.execute(sql, params).fetchall()

def save_job(data):
    with connect_db() as conn:
        cur = conn.execute("""
        INSERT INTO jobs
        (title, category, description, city, pay, employer, phone, email,
         latitude, longitude, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["title"], data["category"], data["description"], data["city"],
            data["pay"], data["employer"], data["phone"], data["email"],
            data["latitude"], data["longitude"],
            datetime.now().isoformat(timespec="seconds")
        ))
        return cur.lastrowid

def save_application(job_id, name, phone, note):
    with connect_db() as conn:
        conn.execute("""
        INSERT INTO applications
        (job_id, applicant_name, applicant_phone, note, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (job_id, name.strip(), phone.strip(), note.strip(),
              datetime.now().isoformat(timespec="seconds")))

def fetch_applications():
    with connect_db() as conn:
        return conn.execute("""
        SELECT a.*, j.title, j.city, j.employer
        FROM applications a LEFT JOIN jobs j ON j.id = a.job_id
        ORDER BY a.id DESC
        """).fetchall()

init_db()

# -------------------- Location and AI helpers --------------------
def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(min(1, math.sqrt(a)))

def geocode_place(place):
    # Nominatim geocoding; use sparingly and only for user-entered areas.
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "WorkSortageColabDemo/1.0"},
            timeout=12,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    return None, None

def ask_gemma(question, language_name, history):
    instruction = LANGUAGES[language_name]["instruction"]
    messages = [{
        "role": "system",
        "content": (
            "You are WorkSortage, a helpful assistant for daily-wage workers. "
            "Give short, practical, safe advice about finding work, contacting employers, "
            "and using this website. Do not claim to have searched the database. "
            + instruction
        )
    }]
    for item in history[-6:]:
        if item.get("role") in ("user", "assistant"):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": question})
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()

def text_to_speech(text, language_name):
    audio = BytesIO()
    gTTS(text=text, lang=LANGUAGES[language_name]["tts"]).write_to_fp(audio)
    audio.seek(0)
    return audio.read()

# -------------------- Sidebar and header --------------------
with st.sidebar:
    st.markdown("# 🧰 WorkSortage")
    language_name = st.selectbox("Language / భాష / भाषा", list(LANGUAGES), key="selected_language")
    st.caption(T("Your local job companion"))
    page_labels = {
        "🔎 Find Jobs": "🔎 " + T("Find Jobs"),
        "🎙️ Voice Assistant": "🎙️ " + T("Voice Assistant"),
        "➕ Post a Job": "➕ " + T("Post a Job"),
        "📋 My Applications": "📋 " + T("My Applications"),
    }
    page = st.radio("Navigate" if language_name == "English" else T("Navigate"), list(page_labels), format_func=lambda value: page_labels[value])
    st.divider()
    st.caption(T("Simple • Local • Worker-friendly"))

st.markdown(f"""
<div class="hero">
  <h1>🧰 WorkSortage</h1>
  <p>{T("Find nearby work. Contact employers. Apply with confidence.")}</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Find jobs --------------------
if page == "🔎 Find Jobs":
    st.subheader("🔎 " + T("Find jobs near you"))
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 " + T("Search jobs"), placeholder=T("Helper, delivery, cleaner..."))
    with col2:
        category_label = st.selectbox("🧩 " + T("Job field"), ["All categories"] + list(CATEGORIES), format_func=lambda value: ("All categories" if value == "All categories" else CATEGORY_ICONS.get(CATEGORIES.get(value, value), "🧰") + " " + T(CATEGORIES.get(value, value))) if value != "All categories" else T(value))
    category = "All categories" if category_label == "All categories" else CATEGORIES[category_label]

    with st.expander("📍 " + T("Current location and distance"), expanded=True):
        st.write(T("Click the location control and allow location permission in your browser."))
        location_data = streamlit_geolocation()
        if isinstance(location_data, dict):
            lat = location_data.get("latitude")
            lon = location_data.get("longitude")
            if lat is not None and lon is not None:
                st.session_state["user_lat"] = float(lat)
                st.session_state["user_lon"] = float(lon)
                st.success(T("Current location received."))
        radius = st.slider(T("Maximum distance (km)"), min_value=1, max_value=100, value=25)
        manual_place = st.text_input(T("Or enter a town / area"), placeholder=T("Example: Kakinada"))
        if st.button(T("Find this area")):
            if manual_place.strip():
                with st.spinner(T("Looking up area...")):
                    coords = geocode_place(manual_place.strip())
                if coords[0] is None:
                    st.warning(T("Area not found. Try a more specific place."))
                else:
                    st.session_state["user_lat"], st.session_state["user_lon"] = coords
                    st.success(T("Area location set."))

    user_lat = st.session_state.get("user_lat")
    user_lon = st.session_state.get("user_lon")
    jobs = fetch_jobs(category, search)
    visible = []
    for job in jobs:
        km = None
        if (user_lat is not None and user_lon is not None
            and job["latitude"] is not None and job["longitude"] is not None):
            km = haversine_km(user_lat, user_lon, job["latitude"], job["longitude"])
            if km > radius:
                continue
        visible.append((job, km))
    visible.sort(key=lambda pair: (pair[1] is None, pair[1] if pair[1] is not None else 0))

    if not visible:
        st.info(T("No matching jobs found. Try a different search or post a job."))
    for job, km in visible:
        icon = CATEGORY_ICONS.get(job["category"], "🧰")
        with st.container(border=True):
            st.markdown(f"### {icon} {job['title']}")
            distance_text = f" · {km:.1f} km away" if km is not None else ""
            st.caption(f"{CATEGORY_ICONS.get(job['category'], '🧰')} {T(job['category'])} · 📍 {job['city']}{distance_text}")
            st.write(job["description"])
            left, right = st.columns(2)
            with left:
                st.markdown(f"**💰 {T('Pay')}:** {job['pay']}")
                st.markdown(f"**🏢 {T('Employer')}:** {job['employer']}")
            with right:
                if job["phone"]:
                    safe_phone = "".join(ch for ch in job["phone"] if ch.isdigit() or ch in "+-() ")
                    st.markdown(f"[📞 {T('Call employer')}](tel:{safe_phone})")
                if job["email"]:
                    safe_email = html.escape(job["email"])
                    st.markdown(f"[✉️ {T('Email employer')}](mailto:{safe_email})")
                if not job["phone"] and not job["email"]:
                    st.caption(T("No contact details provided."))
            with st.expander("📝 " + T("Apply for this job")):
                with st.form(f"apply_{job['id']}"):
                    applicant_name = st.text_input(T("Your name"))
                    applicant_phone = st.text_input(T("Your phone number"))
                    note = st.text_area(T("Message (optional)"))
                    submitted = st.form_submit_button(T("Submit application"))
                if submitted:
                    if not applicant_name.strip() or not applicant_phone.strip():
                        st.error(T("Please enter your name and phone number."))
                    else:
                        save_application(job["id"], applicant_name, applicant_phone, note)
                        st.success(T("Application saved in this demo. Please also contact the employer directly."))

# -------------------- Voice assistant --------------------
elif page == "🎙️ Voice Assistant":
    st.subheader("🎙️ " + T("Voice Assistant"))
    st.write(T("Speak or type a question. Choose Telugu or Hindi from the language menu."))

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    for item in st.session_state["chat_history"]:
        with st.chat_message(item["role"]):
            st.write(item["content"])

    spoken_text = speech_to_text(
        language=LANGUAGES[language_name]["stt"],
        use_container_width=True,
        just_once=True,
        key=f"speech_{language_name}",
    )
    if spoken_text:
        st.session_state["voice_question"] = spoken_text

    question = st.text_area(
        T("Your question"),
        value=st.session_state.get("voice_question", ""),
        placeholder=T("Ask about jobs or using WorkSortage...")
    )
    c1, c2 = st.columns(2)
    with c1:
        ask = st.button("✨ " + T("Ask Gemma AI"), type="primary", use_container_width=True)
    with c2:
        clear = st.button("🧹 " + T("Clear conversation"), use_container_width=True)

    if clear:
        st.session_state["chat_history"] = []
        st.session_state["voice_question"] = ""
        st.session_state.pop("last_answer", None)
        st.rerun()

    if ask:
        if not question.strip():
            st.warning(T("Please speak or type a question."))
        else:
            history = st.session_state["chat_history"].copy()
            st.session_state["chat_history"].append({"role": "user", "content": question.strip()})
            try:
                with st.spinner(T("Gemma is thinking...")):
                    answer = ask_gemma(question.strip(), language_name, history)
                st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                st.session_state["last_answer"] = answer
                st.session_state["voice_question"] = ""
            except requests.RequestException as exc:
                st.error(T("Cannot reach Ollama. Check that Ollama is running and Gemma is installed."))
                st.caption(str(exc))
            st.rerun()

    if st.session_state.get("last_answer"):
        if st.button("🔊 " + T("Speak latest answer")):
            try:
                with st.spinner(T("Preparing audio...")):
                    audio_data = text_to_speech(st.session_state["last_answer"], language_name)
                st.audio(audio_data, format="audio/mp3")
            except Exception as exc:
                st.error(T("Text-to-speech failed: ") + str(exc))

# -------------------- Post a job --------------------
elif page == "➕ Post a Job":
    st.subheader("➕ " + T("Post a Job"))
    st.write(T("Employers can add local work opportunities."))
    with st.form("post_job_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            title = st.text_input(T("Job title *"))
            category_label = st.selectbox(T("Job field"), list(CATEGORIES), format_func=lambda value: CATEGORY_ICONS.get(CATEGORIES.get(value, value), "🧰") + " " + T(CATEGORIES.get(value, value)))
            city = st.text_input(T("Work area / town *"))
            pay = st.text_input(T("Salary or daily pay *"))
        with right:
            employer = st.text_input(T("Employer name *"))
            phone = st.text_input(T("Contact phone"))
            email = st.text_input(T("Contact email"))
        description = st.text_area(T("Job details *"))
        st.caption(T("Coordinates are optional, but required for exact distance calculations."))
        x, y = st.columns(2)
        with x:
            lat_text = st.text_input(T("Job latitude (optional)"))
        with y:
            lon_text = st.text_input(T("Job longitude (optional)"))
        post = st.form_submit_button("🚀 " + T("Publish job"), type="primary", use_container_width=True)

    if post:
        if not all(v.strip() for v in [title, city, pay, employer, description]):
            st.error(T("Please complete all required fields."))
        else:
            try:
                job_lat = float(lat_text) if lat_text.strip() else None
                job_lon = float(lon_text) if lon_text.strip() else None
                if (job_lat is None) != (job_lon is None):
                    st.error(T("Enter both coordinates or leave both blank."))
                    st.stop()
                if job_lat is not None and not (-90 <= job_lat <= 90 and -180 <= job_lon <= 180):
                    st.error(T("Coordinates are outside the valid range."))
                    st.stop()
                job_id = save_job({
                    "title": title.strip(),
                    "category": CATEGORIES[category_label],
                    "description": description.strip(),
                    "city": city.strip(),
                    "pay": pay.strip(),
                    "employer": employer.strip(),
                    "phone": phone.strip(),
                    "email": email.strip(),
                    "latitude": job_lat,
                    "longitude": job_lon,
                })
                st.success(f"Job #{job_id} " + T("Job published successfully!"))
            except ValueError:
                st.error(T("Latitude and longitude must be valid numbers."))

# -------------------- Applications --------------------
elif page == "📋 My Applications":
    st.subheader("📋 " + T("My Applications"))
    applications = fetch_applications()
    if not applications:
        st.info(T("You have not applied for any jobs yet."))
    for app in applications:
        with st.container(border=True):
            st.markdown(f"### 📝 {app['title'] or 'Job no longer available'}")
            st.caption(f"📍 {app['city'] or T('Unknown area')} · 🏢 {app['employer'] or T('Unknown employer')}")
            st.write(f"**{T('Name:')}** {app['applicant_name']}")
            st.write(f"**{T('Phone:')}** {app['applicant_phone']}")
            st.write(f"**{T('Message:')}** {app['note'] or '—'}")
            st.caption(f"{T('Submitted:')} {app['created_at']}")

st.divider()
st.caption(
    "WorkSortage demo. " + T("Listings and applications are saved in this Colab runtime.") + " "
    + T("This version is not yet connected to your friend's FastAPI backend.")
)
