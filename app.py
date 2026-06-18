import streamlit as st
import base64
from streamlit_option_menu import option_menu
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import mediapipe as mp
import numpy as np
import time
from datetime import datetime, timedelta
import json
import os
from music.music import music_page
from settings.settings import settings_page
from groq import Groq
import pyttsx3
import threading

st.set_page_config(
    page_title="AI Virtual Fitness Trainer",
    layout="wide",
    initial_sidebar_state="expanded"
)

def save_log():
    with open("session_log.json", "w") as f:
        json.dump(st.session_state.session_log, f, indent=4)
def save_food_log():
    with open("food_log.json", "w") as f:
        json.dump(st.session_state.food_log, f)
def save_streak():
    with open("streak.json", "w") as f:
        json.dump({
            "streak":  st.session_state.prog_streak,
            "updated": st.session_state.streak_updated
        }, f)
def save_user_goals():
    with open("user_goals.json", "w") as f:
        json.dump(st.session_state.user_goals, f)
def persist_progress():
    with open("goals_vals.json", "w") as f:
        json.dump(st.session_state.goals_vals, f)
def save_weight():
    with open("weight_log.json", "w") as f:
        json.dump(st.session_state.weight_log, f)
def save_custom_targets():
    with open("custom_targets.json", "w") as f:
        json.dump(st.session_state.custom_targets, f)
@st.cache_data
def load_video(video_path):
    if not os.path.exists(video_path):
        return None
    with open(video_path, "rb") as f:
        import base64
        return base64.b64encode(f.read()).decode()

# ── Welcome screen ────────────────────────────────────────────────────────────
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False
# ── User Profile Check ────────────────────────────────────────────────────────
if "user_profile" not in st.session_state:
    if os.path.exists("user_profile.json"):
        with open("user_profile.json", "r") as f:
            st.session_state.user_profile = json.load(f)
    else:
        st.session_state.user_profile = None

if st.session_state.user_profile is None:

    st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: stretch !important;
    }
    [data-testid="stColumn"] {
        display: flex !important;
    }
    [data-testid="stColumn"] > div {
        width: 100% !important;
    }
    .split-left {
        background: linear-gradient(160deg, #0d1b3e 0%, #1a3a6b 100%);
        padding: 20px 40px;
        min-height: 94vh;
        color: white;
        border-top-left-radius:12px;
        border-bottom-left-radius:12px;
    }
    .split-logo {
        font-size: 3.2rem;
        font-weight: 800;
        color: #ffff;
    }
    .split-heading {
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 10px;
        color: #DBEAFE;
    }
    .split-heading span {
        color: #66C2FF;
    } 
    .split-desc {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.7);
        line-height: 1.6;
        margin-bottom: 25px;
    }
    .feature-item {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .feature-check {
        width: 26px;
        height: 26px;
        border-radius: 50%; 
        
        background: rgba(96,165,250,0.15);
        color: #60a5fa;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 0.8rem;
        font-weight: 700;

        flex-shrink: 0;
    }
    .feature-text-title {
        font-size: 1rem;
        font-weight: 600;
    }

    .feature-text-sub {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.6);
    }
    .split-quote {
        margin-top: 40px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 20px;
    }

    .split-quote p {
        font-size: 0.8rem;
        font-style: italic;
        color: rgba(255,255,255,0.6);
    }
    [data-testid="stColumn"]:nth-child(2) {
        background: #ffffff;
        padding: 20px 40px;
        min-height: 94vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-top-right-radius:12px;
        border-bottom-right-radius:12px;
    }
    .form-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0d1b3e;
    }
    .form-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 5px;
    }
    .ob-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #0d1b3e;
        margin-bottom: 6px;
        margin-top: 14px;
    }
    /* main dropdown box */
    div[data-testid="stSelectbox"] > div > div {
        background: #f8fafc !important;
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stSelectbox"] > div > div:hover {
        border: 1.5px solid #94a3b8 !important;
    }
    div[data-testid="stSelectbox"] div[aria-invalid="true"] {
        border: 1.5px solid #e2e8f0 !important;
        box-shadow: none !important;
    }
    button[kind="primary"] {
        background: #0d1b3e !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 12px !important;
        transition: 0.2s ease !important;
        border:none;
    }
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
    }
    .ob-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 20px 0;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        box-shadow: none !important;
        border: none !important;
    }
    /* pura header hide */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* toolbar (Deploy, settings, etc.) */
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* hamburger / menu button */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
    }
    [data-testid="stHorizontalBlock"] {
        margin-top: -80px !important;
    }
    """,unsafe_allow_html=True)

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        st.markdown("""
        <div class="split-left">
            <div class="split-logo">FitAI</div>
            <div class="split-heading">Train Smarter.<br><span>Move Better.</span></div>
            <div class="split-desc">
                Your personal AI trainer that tracks your reps,
                corrects your form, and helps you train smarter
                — all from your webcam.
            </div>
            <div class="feature-item">
                <div class="feature-check">✔</div>
                <div>
                    <div class="feature-text-title">AI Powered Tracking</div>
                    <div class="feature-text-sub">Real-time pose detection and rep counting via webcam</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-check">✔</div>
                <div>
                    <div class="feature-text-title">Live Voice Feedback</div>
                    <div class="feature-text-sub">AI trainer gives motivating feedback on every rep</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-check">✔</div>
                <div>
                    <div class="feature-text-title">Progress Analytics</div>
                    <div class="feature-text-sub">Track your workouts, nutrition and daily goals</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-check">✔</div>
                <div>
                    <div class="feature-text-title">Music While Training</div>
                    <div class="feature-text-sub">Upload and play your favorite workout songs</div>
                </div>
            </div>
            <div class="split-quote">
                <p>"The only bad workout is the one that didn't happen."</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with right_col:
        st.markdown("""
        <div class="form-title">Create Your Profile</div>
        <div class="form-sub">Let's customize your fitness experience</div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ob-label">Full Name</div>', unsafe_allow_html=True)
        name = st.text_input(
            "Name",
            placeholder="Enter your full name",
            label_visibility="collapsed"
        )

        st.markdown('<div class="ob-label">Current Weight (kg)</div>', unsafe_allow_html=True)
        weight = st.text_input(
            "Weight",
            value="0.0",
            label_visibility="collapsed"
        )

        try:
            weight = round(float(weight), 1)
        except:
            st.error("Enter valid weight")
            
        st.markdown("""
        <div class="ob-label">Activity Level 
            <span style="color:#94a3b8; font-weight:400;">
                (Beginner / Intermediate / Advanced)
            </span>
        </div>
        """, unsafe_allow_html=True)
        level = st.selectbox(
            "Level",
            ["Beginner", "Intermediate", "Advanced"],
            label_visibility="collapsed"
        )

        st.markdown("""
        <div class="ob-label">Fitness Goal
            <span style="color:#94a3b8; font-weight:400;">
                (Weight Loss / Muscle Gain / Stay Fit / Endurance)
            </span>
        </div>
        """, unsafe_allow_html=True)
        goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Muscle Gain", "Stay Fit", "Endurance"],
            label_visibility="collapsed"
        )

        st.markdown('<div class="ob-divider"></div>', unsafe_allow_html=True)

        if st.button("Continue →", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("Please enter your name!")
            else:
                profile = {
                    "name":   name.strip(),
                    "weight": weight,
                    "goal":   goal,
                    "level":  level
                }
                with open("user_profile.json", "w") as f:
                    json.dump(profile, f)
                st.session_state.user_profile = profile
                st.rerun()

    st.stop()

if not st.session_state.welcomed:

    with open("images/welcome.jpg", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    st.markdown("""
    <style>
    [data-testid="stSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapse"] { display: none !important; }
    [data-testid="stMain"]            { padding: 0 !important; }
    [data-testid="block-container"]   { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"]   { gap: 0 !important; padding: 0 !important; }
    .element-container                { margin: 0 !important; padding: 0 !important; }
    html, body { overflow: hidden !important; height: 100vh !important; }
    /* pura header hide */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* toolbar (Deploy, settings, etc.) */
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* hamburger / menu button */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');

    .welcome-wrap {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        height: 88vh;
        width: 100%;
        text-align: left;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        position: relative;
        overflow: hidden;
        padding: 0 0 0 8%;
        border-radius:12px;
        margin-top: -40px;
    }}
    .welcome-wrap::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to right,
            rgba(0,0,0,0.65) 0%,
            rgba(0,0,0,0.3) 50%,
            rgba(0,0,0,0.0) 100%
        );
        z-index: 0;
    }}
    .welcome-wrap > * {{
        position: relative;
        z-index: 1;
    }}
    .welcome-content {{
        max-width: 420px;
        margin-top: -25vh;
    }}
    .welcome-title {{
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 6.4rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 12px;
        text-align: left;
    }}
    .welcome-title span {{ 
        color: #66C2FF;
    }}
    .welcome-sub {{
        color: rgba(255,255,255,0.75);
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 0;
        font-family: 'Inter', sans-serif;
        text-align: left;
    }}

    /* ── Pull button up into the image ── */
    [data-testid="stButton"] {{
        margin-top: -22vh !important;
        margin-left: 14vh !important;
        position: relative !important;
        z-index: 10 !important;
    }}
    [data-testid="stButton"] > button {{
        background-color: #102a5c !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        letter-spacing: 0.5px !important;
        padding: 14px 48px !important;
        transition: all 0.15s !important;
    }}
    [data-testid="stButton"] > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
    }} 
    </style>

    <div class="welcome-wrap">
        <div class="welcome-content">
            <div class="welcome-title">Welcome to<br><span>FitAI</span></div>
            <div class="welcome-sub">
                Your personal AI trainer that tracks your reps,
                corrects your form, and helps you train smarter
                — all from your webcam.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶  Get Started"):
        st.session_state.welcomed = True
        st.rerun()

    st.stop()

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

# ── AI Voice Coach ────────────────────────────────────────────────────────────
_groq_client = Groq(api_key="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")

def _speak(text):
    def run():
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    threading.Thread(target=run, daemon=True).start()

def get_ai_feedback(exercise, reps):
    try:
        profile = st.session_state.get("user_profile") or {}
        level   = profile.get("level", "Beginner")
        goal    = profile.get("goal",  "Stay Fit")
        name    = profile.get("name",  "Athlete")

        system_prompt = (
            f"You are FitAI, a personal AI fitness trainer. "
            f"The user's name is {name}, fitness level is {level}, and goal is {goal}. "
            f"Give very short (1-2 sentence) motivating, personalized feedback based on their level and goal. "
            f"For Beginners be encouraging and gentle. For Advanced users be intense and push them harder. "
            f"Tailor advice to their goal: Weight Loss = mention burn/effort, "
            f"Muscle Gain = mention form/squeeze, Endurance = mention pacing/breathing. "
            f"No emojis. Address them by name occasionally."
        )

        response = _groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": f"Exercise: {exercise}, Reps completed: {reps}"}
            ],
            max_tokens=60
        )
        return response.choices[0].message.content
    except:
        return f"Great job! {reps} reps done!"

# ---------- Sidebar ----------
with st.sidebar:
    if "logo_base64" not in st.session_state:
        with open("images/logo.png", "rb") as f:
            st.session_state.logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;
                    padding:10px 4px 20px 4px;
                    height:64px;overflow:hidden;">
            <img src="data:image/png;base64,{st.session_state.logo_base64}"
                 width="64" height="64"
                 style="border-radius:50%;flex-shrink:0;object-fit:contain;">
            <div class="sidebar-brand">Train With FitAI</div>
        </div>
    """, unsafe_allow_html=True)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    nav_options = ["Home", "Exercises", "Progress", "Live Webcam", "Music", "Settings"]
    nav_index   = nav_options.index(st.session_state.current_page)

    selected = option_menu(
        menu_title=None,
        options=nav_options,
        icons=["houses", "activity", "bar-chart-fill", "camera-video", "music-note-beamed", "gear"],
        default_index=nav_index,
        key=f"menu_{st.session_state.current_page}",  # ✅ forces re-render on page change
        orientation="vertical",
        styles={
            "container": {
                "background-color": "#ffffff",
                "padding": "0px",
                "margin": "0px",
            },
            "nav-link": {
                "font-size": "14px",
                "color": "#6b7280",
                "padding": "12px 16px",
                "border-radius": "10px",
                "margin": "2px 0px",
                "font-weight": "500",
            },
            "nav-link-selected": {
                "background-color": "#eef2ff",
                "color": "#4f6ef7",
                "font-weight": "600",
                "border-radius": "10px",
            },
            "icon": { "color": "inherit" },
        }
    )

    # ✅ Menu click updates current_page
    st.session_state.current_page = selected

# ✅ Use current_page everywhere instead of page
page = st.session_state.current_page

# ── Sidebar CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&display=swap');

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e8edf5 !important;
    box-shadow: 2px 0 20px rgba(0,0,0,0.06) !important;
}
[data-testid="stSidebarResizeHandle"] {
    display: none !important;
}
[data-testid="stSidebar"] .stMarkdown:first-child > div {
    min-height: 64px !important;
    height: 64px !important;
    overflow: hidden !important;
}
.sidebar-brand {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    color: #1a1f36 !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    line-height: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Pages ----------
if page == "Home":

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] > [data-testid="stMain"] {
        background: #f0f4ff;
    }
    [data-testid="block-container"] {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    .hero {
        background: linear-gradient(120deg, #0d1b3e 55%, #1a3a6b 100%);
        border-radius: 20px;
        padding: 44px 40px;
        margin: -50px 0 20px 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.75);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
        font-family: 'Inter', sans-serif;
    }
    .hero-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 12px;
    }
    .hero-title span { color: #66C2FF; }
    .hero-sub {
        color: rgba(255,255,255,0.65);
        font-size: 0.92rem;
        line-height: 1.6;
        margin-bottom: 8px;
        font-family: 'Inter', sans-serif;
        max-width: 480px;
    }
    .hero-stats {
        display: flex;
        gap: 12px;
        margin-top: 24px;
    }
    .stat-pill {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 10px 18px;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    .stat-pill .num {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .stat-pill .lbl {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.5);
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    .section-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #0d1b3e;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 0.82rem;
        color: #6b7a99;
        margin-bottom: 16px;
        font-family: 'Inter', sans-serif;
    }
    .features-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 24px;
    }
    .feat-card {
        background: #ffffff;
        border: 1px solid #e4eaf5;
        border-radius: 16px;
        padding: 20px;
        font-family: 'Inter', sans-serif;
        transition: all 0.15s ease;
    }
    .feat-card:hover {
        border-color: rgba(100,120,255,0.3);
        box-shadow: 0 4px 20px rgba(100,120,255,0.1);
        transform: translateY(-2px);
    }
    .feat-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .feat-title {
        font-weight: 700;
        font-size: 0.92rem;
        color: #0d1b3e;
        margin-bottom: 4px;
    }
    .feat-desc {
        font-size: 0.78rem;
        color: #6b7a99;
        line-height: 1.5;
    }
    .feat-tag {
        display: inline-block;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 10px;
    }
    .steps-card {
        background: #ffffff;
        border: 1px solid #e4eaf5;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }
    .steps-row {
        display: flex;
        gap: 0;
        margin-top: 20px;
    }
    .step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    .step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 19px;
        left: 55%;
        width: 90%;
        height: 2px;
        background: #e4eaf5;
    }
    .step-dot {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px;
        font-weight: 800;
        font-size: 0.9rem;
        position: relative;
        z-index: 1;
    }
    .step-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #0d1b3e;
    }
    .step-sub {
        font-size: 0.7rem;
        color: #6b7a99;
        margin-top: 3px;
    }
    .cta-banner {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        margin-bottom: 10px;
    }
    .cta-banner h3 {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: #fff;
        margin-bottom: 8px;
    }
    .cta-banner p {
        color: rgba(255,255,255,0.7);
        font-size: 0.88rem;
        margin-bottom: 20px;
    }
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 32px !important;
        width: auto !important;
        transition: all 0.15s !important;
        margin-top: 12px !important;
    }
    [data-testid="stButton"] > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <div class="hero-badge">✦ AI-Powered Fitness</div>
        <div class="hero-title">Train Smarter.<br><span>Move Better.</span></div>
        <div class="hero-sub">
            Real-time posture detection, rep counting, and
            personalized feedback — all from your webcam.
        </div>
        <div class="hero-stats">
            <div class="stat-pill">
                <div class="num">7+</div>
                <div class="lbl">Exercises</div>
            </div>
            <div class="stat-pill">
                <div class="num">Live</div>
                <div class="lbl">AI Feedback</div>
            </div>
            <div class="stat-pill">
                <div class="num">0ms</div>
                <div class="lbl">Setup needed</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">Why Choose FitAI?</div>
    <div class="section-sub">Everything you need for smarter, safer workouts</div>
    <div class="features-grid">
        <div class="feat-card">
            <div class="feat-icon" style="background:#e8f4ff">🧠</div>
            <div class="feat-title">AI Posture Detection</div>
            <div class="feat-desc">MediaPipe tracks 33 body landmarks in real-time to detect your form on every rep.</div>
            <span class="feat-tag" style="background:#e8f4ff;color:#185FA5">Real-time</span>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:#e8fff4">📊</div>
            <div class="feat-title">Automatic Rep Counter</div>
            <div class="feat-desc">Angle-based counting with smoothing — no false reps, no missed reps.</div>
            <span class="feat-tag" style="background:#e8fff4;color:#0F6E56">Accurate</span>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:#fff0f0">🎯</div>
            <div class="feat-title">Live Form Feedback</div>
            <div class="feat-desc">Get instant corrections so you train safely and effectively every session.</div>
            <span class="feat-tag" style="background:#fff0f0;color:#A32D2D">Smart</span>
        </div>
        <div class="feat-card">
            <div class="feat-icon" style="background:#f5f0ff">📈</div>
            <div class="feat-title">Progress Tracking</div>
            <div class="feat-desc">Visualize your workout history, reps, and improvement over time.</div>
            <span class="feat-tag" style="background:#f5f0ff;color:#534AB7">Analytics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="steps-card">
        <div class="section-title" style="margin-bottom:2px">How It Works</div>
        <div class="section-sub">3 steps to smarter training</div>
        <div class="steps-row">
            <div class="step">
                <div class="step-dot" style="background:#e8f4ff;color:#185FA5">1</div>
                <div class="step-label">Open Webcam</div>
                <div class="step-sub">No setup needed</div>
            </div>
            <div class="step">
                <div class="step-dot" style="background:#e8fff4;color:#0F6E56">2</div>
                <div class="step-label">Pick Exercise</div>
                <div class="step-sub">Curl, squat, pushup</div>
            </div>
            <div class="step">
                <div class="step-dot" style="background:#f5f0ff;color:#534AB7">3</div>
                <div class="step-label">Start Training</div>
                <div class="step-sub">AI tracks everything</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cta-banner">
        <h3>Ready to Train Smarter?</h3>
        <p>Open your webcam and let FitAI guide your workout in real-time.</p>
    </div>
    """, unsafe_allow_html=True)

    col_x, col_y, col_z = st.columns([2, 1, 2])
    with col_y:
        if st.button("▶  Go to Webcam"):
            st.session_state.current_page = "Live Webcam"
            st.rerun()


elif page == "Exercises":

    if "exercise_screen" not in st.session_state:
        st.session_state.exercise_screen = "search"
    if "exercise_query" not in st.session_state:
        st.session_state.exercise_query = ""

    def perform_search():
        if not st.session_state.get("exercise_search", "").strip():
            return  # ← do nothing on empty Enter
        st.session_state.exercise_query = st.session_state.exercise_search
        st.session_state.exercise_screen = "results"

    def go_back():
        st.session_state.exercise_screen = "search"
        st.session_state.exercise_search = ""

    def video_card(video_path):
        b64 = load_video(video_path)
        return f"""
        <div style="position:relative; border-radius:12px 12px 0 0; 
                    overflow:hidden; height:130px;">
            <video 
                style="width:100%; height:100%; object-fit:cover; display:block;"
                controls
                muted
                loop
                preload="auto">
                <source src="data:video/mp4;base64,{b64}" type="video/mp4">
            </video>
        </div>
        """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Search page header ── */
    .exercise-search {
        background-color:#0d1b3e;
        border-radius: 20px;
        padding: 40px 40px;
        text-align: center;
        margin:0 0 20px 0;
    }
    .search-badge {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.75);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
        font-family: 'Inter', sans-serif;
    }
    .exercise-search h1 {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 800;
        font-size: 2.4rem;
        color: #f5f5f5;
    }
    .exercise-search p {
        font-family: 'Inter', sans-serif;
        color: #6b7a99;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    /* ── Info text ── */
    .information p {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 10px;
        text-align: center;
    }
    /* ── Search input ── */
    div[data-testid="stTextInput"] input::placeholder {
        color: #94a3b8;
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Inter', sans-serif !important;
        background-color: white !important;
        color: #0d1b3e !important;
    }

    /* ── Search input shape ── */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border-top-left-radius: 18px !important;
        border-bottom-left-radius: 18px !important;
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        border: 1.5px solid #dde3f5 !important;
        background-color: white !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #0d1b3e !important;
        box-shadow: none !important;
    }
    /* ── Search arrow button ── */
    button[kind="secondary"] {
        background-color: #0d1b3e !important;
        color: white !important;
        border-top-right-radius: 18px !important;
        border-bottom-right-radius: 18px !important;
        border-top-left-radius: 0 !important;
        border-bottom-left-radius: 0 !important;
        margin: 0 0 0 -10px;
        border: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #1a3a6b !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }

    /* ── Back button ── */
    button[kind="primary"] {
        background-color: #0d1b3e !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        background-color: #1a3a6b !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }

    /* ── Results header ── */
    .results-header {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #0d1b3e;
        margin: 4px 0 16px 0;
    }
    /* ── Exercise card ── */
    .ex-card {
        background: #ffffff;
        border: 1px solid #e4eaf5;
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 12px 14px 14px;
        font-family: 'Inter', sans-serif;
        transition: box-shadow 0.15s;
    }
    .ex-card:hover {
        box-shadow: 0 6px 20px rgba(79,110,247,0.1);
    }
    .ex-card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 6px;
        margin-bottom: 6px;
    }
    .ex-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        color: #0d1b3e;
        line-height: 1.2;
    }
    .diff-badge {
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 8px;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .ex-desc {
        font-size: 0.75rem;
        color: #6b7a99;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    .ex-tags { display: flex; gap: 5px; flex-wrap: wrap; }
    .ex-tag {
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 8px;
        background: #eef2ff;
        color: #4f6ef7;
    }
    video.stVideo {
        width: 100% !important;
        height: 130px !important;
        object-fit: cover !important;
        border-radius: 12px 12px 0 0 !important;
        display: block !important;
    }

    div[data-testid="stVideo"] {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        border-radius: 12px 12px 0 0 !important;
    }

    div[data-testid="stElementContainer"]:has(video.stVideo) {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 0 !important;
    }
    /* Video aur card ke beech gap hatao */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stElementContainer"]:has(video.stVideo) + div[data-testid="stElementContainer"] {
        margin-top: -16px !important;
    }
    video::-webkit-media-controls-mute-button { display: none !important; }
    video::-webkit-media-controls-volume-slider { display: none !important; }
    video::-webkit-media-controls-fullscreen-button { display: none !important; }
    video::-webkit-media-controls-download-button { display: none !important; }
    video::-webkit-media-controls-timeline { display: none !important; }
    video::-webkit-media-controls-current-time-display { display: none !important; }
    video::-webkit-media-controls-time-remaining-display { display: none !important; } 
    </style>
    """, unsafe_allow_html=True)
    # ── Search screen ─────────────────────────────────────────────────────────
    if st.session_state.exercise_screen == "search":
        with st.container():
            st.markdown("""
            <div class="exercise-search">
                <div class="search-badge">Exercise Library</div>
                <h1>Find Your Perfect Exercise</h1>
                <p>Search by muscle group and train with proper form.</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([20, 1], gap="small")
        with col1:
            st.text_input(
                "",
                placeholder="Search Exercises such as chest,back,..etc",
                label_visibility="collapsed",
                key="exercise_search",
                on_change=perform_search
            )
        with col2:
            st.button("➤", key="search_btn",
                      use_container_width=True, on_click=perform_search)

        st.markdown("""
        <div class="information">
            <p>Explore exercise demonstrations with guided videos,
            correct posture cues, and clear explanations designed
            to help beginners train safely and effectively.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Results screen ────────────────────────────────────────────────────────
    elif st.session_state.exercise_screen == "results":
        st.button("⮜ Back", on_click=go_back, type="primary")

        query = st.session_state.exercise_query.lower()

        st.markdown(
            f'<div class="results-header">Exercises for {query.capitalize()}</div>',
            unsafe_allow_html=True
        )

        exercises_db = {
            "chest": [
                {
                    "title": "Push-Ups",
                    "desc": "Bodyweight exercise targeting chest, shoulders and arms. Maintain straight posture throughout.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Chest", "No Equipment"],
                    "video": "videos/Chest/Pushup.mp4",
                },
                {
                    "title": "Flat Bench Press",
                    "desc": "Compound movement that builds strength and size in chest, shoulders, and triceps.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Chest", "Barbell"],
                    "video": "videos/Chest/Flat_Bench_Press.mp4",
                },
                {
                    "title": "Incline Bench Press",
                    "desc": "Targets the upper chest, shoulders and triceps for better chest definition.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Upper Chest", "Barbell"],
                    "video": "videos/Chest/Incline_Bench_Press.mp4",
                },
                {
                    "title": "Cable Fly",
                    "desc": "Isolation exercise targeting the chest with constant cable tension. Perfect for building chest definition and muscle separation.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Chest", "Cable Machine"],
                    "video": "videos/Chest/Cable_Fly.mp4",
                },
            ],
            "back": [
                {
                    "title": "Pull-Ups",
                    "desc": "Upper body compound movement targeting lats, biceps and rear delts.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Back", "No Equipment"],
                    "video": "videos/Back/Pull_Ups.mp4",
                },
                {
                    "title": "Deadlift",
                    "desc": "Full body compound lift primarily targeting lower and upper back, glutes and hamstrings.",
                    "diff": "Advanced",
                    "diff_bg": "rgba(255,82,82,0.1)",
                    "diff_color": "#ff5252",
                    "tags": ["Back", "Barbell"],
                    "video": "videos/Back/Deadlift.mp4",
                },
                {
                    "title": "Lat Pulldown",
                    "desc": "Machine exercise that targets the latissimus dorsi for a wider back.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Back", "Machine"],
                    "video":"videos/Back/Lat_Pulldown.mp4",
                },
                {
                    "title": "Bent Over Row",
                    "desc": "Compound pulling movement targeting the entire back and rear delts.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Back", "Barbell / Cable"],
                    "video": "videos/Back/Bent_Over_Row.mp4",
                },
            ],
            "legs": [
                {
                    "title": "Squats",
                    "desc": "King of leg exercises targeting quads, hamstrings, glutes and core.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "No Equipment"],
                    "video": "videos/Legs/Squats.mp4",
                },
                {
                    "title": "Lunges",
                    "desc": "Unilateral leg exercise targeting quads, hamstrings and glutes.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "No Equipment"],
                    "video": "videos/Legs/Lunges.mp4",
                },
                {
                    "title": "Leg Press",
                    "desc": "Machine compound movement targeting quads, hamstrings and glutes safely.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "Machine"],
                    "video":"videos/Legs/Leg_Press.mp4",
                },
                {
                    "title": "Smith Machine Squat",
                    "desc": "Guided squat movement on smith machine targeting quads, hamstrings and glutes with added stability and safety.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "Machine"],
                    "video":"videos/Legs/Smith_Machine_Squat.mp4",
                },
            ],
        }

        if query in exercises_db:
            cols = st.columns(4, gap="small")
            for col, ex in zip(cols, exercises_db[query]):
                with col:
                    if ex["video"] and os.path.exists(ex["video"]):
                        st.video(ex["video"])

                    # Card below video
                    tags_html = "".join([
                        f'<span class="ex-tag">{t}</span>'
                        for t in ex["tags"]
                    ])
                    st.markdown(f"""
                    <div class="ex-card">
                        <div class="ex-card-header">
                            <div class="ex-title">{ex["title"]}</div>
                            <span class="diff-badge"
                                  style="background:{ex["diff_bg"]};
                                         color:{ex["diff_color"]}">
                                {ex["diff"]}
                            </span>
                        </div>
                        <div class="ex-desc">{ex["desc"]}</div>
                        <div class="ex-tags">{tags_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No exercises found. Try Chest, Back, or Legs.")

elif page == "Live Webcam":
    mp_pose = mp.solutions.pose

    EXERCISE_CONFIG = {
        "Bicep Curl": {
            "landmarks": {"left":  (11, 13, 15), "right": (12, 14, 16)},
            "up_limit":   40,
            "down_limit": 160,
            "joints":     {11, 12, 13, 14, 15, 16},
            "connections": [(11,13),(13,15),(12,14),(14,16),(11,12)],
        },
        "Pushups": {
            "landmarks": {"left":  (11, 13, 15), "right": (12, 14, 16)},
            "up_limit":   160,
            "down_limit": 90,
            "joints":     {11, 12, 13, 14, 15, 16},
            "connections": [(11,13),(13,15),(12,14),(14,16),(11,12)],
        },
        "Squats": {
            "landmarks": {"left":  (23, 25, 27), "right": (24, 26, 28)},
            "up_limit":   90,
            "down_limit": 160,
            "joints":     {23, 24, 25, 26, 27, 28},
            "connections": [(23,25),(25,27),(24,26),(26,28),(23,24)],
        },
        "Shoulder Press": {
            "landmarks": {"left":  (11, 13, 15), "right": (12, 14, 16)},
            "up_limit":   40,
            "down_limit": 120,
            "joints":     {11, 12, 13, 14, 15, 16},
            "connections": [(11,13),(13,15),(12,14),(14,16),(11,12)],
        },
        "Tricep Dips": {
            "landmarks": {"left":  (11, 13, 15), "right": (12, 14, 16)},
            "up_limit":   160,
            "down_limit": 80,
            "joints":     {11, 12, 13, 14, 15, 16},
            "connections": [(11,13),(13,15),(12,14),(14,16),(11,12)],
        },
        "Lunges": {
            "landmarks": {"left":  (23, 25, 27), "right": (24, 26, 28)},
            "up_limit":   90,
            "down_limit": 160,
            "joints":     {23, 24, 25, 26, 27, 28},
            "connections": [(23,25),(25,27),(24,26),(26,28),(23,24)],
        },
        "Lateral Raise": {
            "landmarks": {"left":  (23, 11, 13), "right": (24, 12, 14)},
            "up_limit":   60,
            "down_limit": 20,
            "joints":     {11, 12, 13, 14, 23, 24},
            "connections": [(11,13),(12,14),(11,23),(12,24),(11,12)],
        },
        "Plank": {
            "landmarks": {"left":  (11, 23, 25), "right": (12, 24, 26)},
            "up_limit":   175,
            "down_limit": 155,
            "joints":     {11, 12, 23, 24, 25, 26},
            "connections": [(11,23),(23,25),(12,24),(24,26),(11,12)],
        },
    }
    SPEED_THRESHOLD = {
        "Bicep Curl": 1.0,
        "Squats": 1.5,
        "Pushups": 0.8,
        "Shoulder Press": 1.2,
        "Tricep Dips": 0.8,
        "Lunges": 1.5,
        "Lateral Raise": 1.0,
        "Plank": 999,
    }
    class VideoProcessor(VideoTransformerBase):

        def __init__(self):
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7,
            )
            self.counter  = 0
            self.stage    = None
            self.exercise = "Bicep Curl"
            self.angle    = 0
            self.feedback = "Get into position"
            self._angle_buffer = []
            self._BUFFER_SIZE  = 5
            self._no_landmark_frames = 0
            self._NO_LANDMARK_LIMIT  = 10
            self.is_speaking = False  
            self.last_rep    = 0     
            self.last_rep_time = None
            self.rep_times = []  
            self.rest_spoken = False 
            self.reached_down = False
            self.rep_quality = "—"
            self.good_reps = 0
            self.total_reps = 0
            self.performance = 0
            self.rep_start_time = None 

        def _smooth_angle(self, raw_angle):
            self._angle_buffer.append(raw_angle)
            if len(self._angle_buffer) > self._BUFFER_SIZE:
                self._angle_buffer.pop(0)
            return sum(self._angle_buffer) / len(self._angle_buffer)

        def _check_visibility(self, lm, indices, threshold=0.5):
            return all(lm[i].visibility > threshold for i in indices)

        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1)
            h, w = img.shape[:2]

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = self.pose.process(rgb)
            rgb.flags.writeable = True

            cfg = EXERCISE_CONFIG[self.exercise]

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                all_joint_ids = list(cfg["joints"])
                if not self._check_visibility(lm, all_joint_ids, threshold=0.5):
                    self._no_landmark_frames += 1
                    if self._no_landmark_frames >= self._NO_LANDMARK_LIMIT:
                        self.stage    = None
                        self.feedback = "Get into position"
                        self._angle_buffer = []
                    self._draw_hud(img, w, h)
                    return img

                self._no_landmark_frames = 0

                def pt(idx):
                    return [lm[idx].x, lm[idx].y]

                li, lj, lk = cfg["landmarks"]["left"]
                ri, rj, rk = cfg["landmarks"]["right"]

                left_angle  = calculate_angle(pt(li), pt(lj), pt(lk))
                right_angle = calculate_angle(pt(ri), pt(rj), pt(rk))
                raw_angle   = max(left_angle, right_angle)

                self.angle   = self._smooth_angle(raw_angle)
                active_joint = pt(rj) if right_angle >= left_angle else pt(lj)

                if self.angle > cfg["down_limit"]:
                    if self.stage != "DOWN":
                        self.stage = "DOWN"
                        self.reached_down = True
                        self.rep_start_time = time.time()
                    self.feedback = "Keep going..."

                elif self.angle < cfg["up_limit"]:
                    if self.stage == "DOWN":
                        self.stage = "UP"
                        self.counter += 1
                        self.total_reps += 1
                        rep_duration = time.time() - self.rep_start_time if self.rep_start_time else 999

                        min_time = SPEED_THRESHOLD.get(self.exercise, 1.0)
                        if self.reached_down and rep_duration >= min_time:
                            self.rep_quality = "Good"
                            self.good_reps += 1
                        else:
                            self.rep_quality = "Bad"

                        if self.total_reps > 0:
                            self.performance = int((self.good_reps / self.total_reps) * 100)

                        self.reached_down = False
                        self.feedback = f"Rep {self.counter} done! ({self.rep_quality})"

                        now = time.time()
                        self.rep_times.append(now - self.last_rep_time if self.last_rep_time else 0)
                        self.last_rep_time = now
                        self.rest_spoken = False

                        if len(self.rep_times) >= 6:
                            avg_last3  = sum(self.rep_times[-3:]) / 3
                            avg_first3 = sum(self.rep_times[:3])  / 3
                            if avg_last3 > avg_first3 * 1.8 and not self.rest_spoken:
                                self.rest_spoken = True
                                threading.Thread(
                                    target=lambda: _speak("You're slowing down, take a breather!"),
                                    daemon=True
                                ).start()

                if self.stage is None:
                    self.feedback = "Get into position"

                # Struggle detection
                if self.stage == "DOWN":
                    if hasattr(self, "last_down_time"):
                        if time.time() - self.last_down_time > 3:
                            _speak("Take it slow, control your movement.")
                    self.last_down_time = time.time()

                for (a, b) in cfg["connections"]:
                    x1 = int(lm[a].x * w); y1 = int(lm[a].y * h)
                    x2 = int(lm[b].x * w); y2 = int(lm[b].y * h)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 200, 0), 2)

                for idx in cfg["joints"]:
                    cx = int(lm[idx].x * w)
                    cy = int(lm[idx].y * h)
                    cv2.circle(img, (cx, cy), 7, (106, 53, 4), -1)
                    cv2.circle(img, (cx, cy), 7, (255, 200, 0), 2)

                ax = int(active_joint[0] * w)
                ay = int(active_joint[1] * h)
                cv2.putText(img, f"{int(self.angle)}°",
                            (ax + 10, ay - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                            (255, 255, 255), 2)
            else:
                self._no_landmark_frames += 1
                if self._no_landmark_frames >= self._NO_LANDMARK_LIMIT:
                    self.stage         = None
                    self.feedback      = "Get into position"
                    self._angle_buffer = []

            if (self.counter > 0 
                and not self.rest_spoken 
                and self.last_rep_time is not None
                and time.time() - self.last_rep_time > 8):
                self.rest_spoken = True
                ex   = self.exercise
                reps = self.counter
                def speak_done(ex=ex, reps=reps):
                    feedback = get_ai_feedback(ex, reps)
                    _speak(f"Great work! You did {reps} reps. {feedback}")
                threading.Thread(target=speak_done, daemon=True).start()

            self._draw_hud(img, w, h)
            return img

        def _draw_hud(self, img, w, h):
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (w, 55), (46,24,2), -1)
            cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
            cv2.putText(img, f"Reps: {self.counter}", (15, 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
            cv2.putText(img, f"{self.exercise}",
                        (w - 20 - len(self.exercise) * 14, 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            stage_color = (210,162,120) if self.stage == "DOWN" else (210,162,120)
            cv2.rectangle(img, (10, h - 45), (110, h - 15), stage_color, -1)
            cv2.putText(img, self.stage or "READY",
                        (18, h - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
        <div class="webcam-header">
            <div class="webcam-badge"><div class="live-dot"></div> Live Tracker</div>
            <div class="webcam-header-title">Live Exercise Tracker</div>
            <div class="webcam-header-sub">Real-time pose detection & rep counting via webcam.</div>
            <div class="webcam-pills">
                <div class="webcam-pill">Pose Detection</div>
                <div class="webcam-pill">Rep Counter</div>
                <div class="webcam-pill">Webcam</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([6, 4], gap="medium")

    with col1:
        if "last_exercise" not in st.session_state:
            st.session_state.last_exercise = "Bicep Curl"

        EXERCISE_LIST = ["All"] + list(EXERCISE_CONFIG.keys())

        exercise_choice = st.selectbox(
            "Select Exercise",
            EXERCISE_LIST,
            key="exercise_select"
        )

        active_exercise = list(EXERCISE_CONFIG.keys())[0] if exercise_choice == "All" else exercise_choice

        tag_map = {
            "All":            ["Full Body", "Mixed"],
            "Bicep Curl":     ["Arms", "Strength"],
            "Pushups":        ["Upper Body", "Strength"],
            "Squats":         ["Legs", "Power"],
            "Shoulder Press": ["Shoulders", "Strength"],
            "Tricep Dips":    ["Arms", "Strength"],
            "Lunges":         ["Legs", "Balance"],
            "Lateral Raise":  ["Shoulders", "Isolation"],
            "Plank":          ["Core", "Stability"],
        }
        pills_css = "⬩".join(tag_map[exercise_choice])
        st.markdown(f"""
        <style>
        [data-testid="stSelectbox"]::after {{
            content: "{pills_css}";
            display: block;
            margin-top: 10px;
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #0d1b3e;
            background: #eef2ff;
            border: 1px solid #c7d2fe;
            border-radius: 999px;
            padding: 3px 10px;
            width: fit-content;
        }}
        </style>
        """, unsafe_allow_html=True)

        # ── Webcam card label ─────────────────────────────────────────────────
        st.markdown("""
            <div class="webcam-card-label">Live Camera</div>
        """, unsafe_allow_html=True)

        # ── Webcam ────────────────────────────────────────────────────────────
        ctx = webrtc_streamer(
            key="exercise-cam",
            video_processor_factory=VideoProcessor,
            media_stream_constraints={
                "video": {
                    "width":     {"ideal": 1280},
                    "height":    {"ideal": 720},
                    "frameRate": {"ideal": 30}
                },
                "audio": False,
            },
            video_html_attrs={
                "style": {
                    "width":         "100%",
                    "border-radius": "10px",
                    "border":        "none",
                },
                "controls": False,
                "autoPlay": True,
            },
            async_processing=True,
        )

        if ctx.video_processor:
            if exercise_choice != st.session_state.last_exercise:
                ctx.video_processor.counter             = 0
                ctx.video_processor.stage               = None
                ctx.video_processor._angle_buffer       = []
                ctx.video_processor._no_landmark_frames = 0
                ctx.video_processor.feedback            = "Get into position"
                st.session_state.last_exercise          = exercise_choice
            ctx.video_processor.exercise = exercise_choice

    # ── Stats panel col2 ─────────────────────────────────────────────────────
    with col2:
        st.markdown("""
            <div class="stats-title">
                <div style="width:7px;height:7px;background:#00e676;border-radius:50%;flex-shrink:0"></div>
                Live Stats
            </div>
        """, unsafe_allow_html=True)

        tips = {
            "Bicep Curl":     "Keep elbows locked at your sides. Full extension down, squeeze at the top.",
            "Pushups":        "Keep your core tight. Lower until elbows hit 90°, push fully back up.",
            "Squats":         "Feet shoulder-width apart. Drive knees out, hips below parallel for a full rep.",
            "Shoulder Press": "Press straight up, lock out at top. Lower slowly to 90°.",
            "Tricep Dips":    "Keep elbows close to body. Lower until 90°, push back up fully.",
            "Lunges":         "Step forward, lower back knee close to floor. Keep front knee over ankle.",
            "Lateral Raise":  "Raise arms to shoulder height, slight bend in elbow. Control the descent.",
            "Plank":          "Keep hips level with shoulders. Breathe steadily and hold the position.",
            "All":            "Select a specific exercise for targeted tips!",
        }
        if ctx.video_processor:
            rep_placeholder      = st.empty()
            stage_angle_ph       = st.empty()
            feedback_placeholder = st.empty()
            progress_placeholder = st.empty()
            tip_placeholder      = st.empty()
            quality_placeholder = st.empty()
            performance_placeholder = st.empty()
            while True:
                proc = ctx.video_processor
                        
                rep_placeholder.markdown(f"""
                <div class="stat-card">
                    <div class="stat-card-label">📈 Rep Counter</div>
                    <div class="stat-card-value">{proc.counter}</div>
                    <div class="stat-card-sub">Total repetitions</div>
                </div>
                """, unsafe_allow_html=True)

                stage_angle_ph.markdown(f"""
                <div class="stat-row">
                    <div class="stat-sm">
                        <div class="stat-sm-label">Stage</div>
                        <div class="stat-sm-val">{proc.stage or "Ready"}</div>
                    </div>
                    <div class="stat-sm">
                        <div class="stat-sm-label">Angle</div>
                        <div class="stat-sm-val">{int(proc.angle)}°</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                feedback_placeholder.markdown(f"""
                <div class="feedback-card">
                    💬 {proc.feedback}
                </div>
                """, unsafe_allow_html=True)

                color = "#9ca3af"  

                if proc.rep_quality == "Good":
                    color = "#00e676"
                elif proc.rep_quality == "Bad":
                    color = "#ff5252"

                quality_placeholder.markdown(f"""
                <div class="quality-card">
                    <div class="quality-label">Rep Quality</div>
                    <div class="quality-value" style="color:{color}">
                        {proc.rep_quality}
                    </div>
                    <div class="quality-sub">Form analysis</div>
                </div>
                """, unsafe_allow_html=True)

                if proc.performance > 80:
                    color = "#00e676"
                elif proc.performance > 50:
                    color = "#ffeb3b"
                else:
                    color = "#ff5252"
                performance_placeholder.markdown(f"""
                <div class="performance-card">
                    <div class="performance-label">Performance</div>
                    <div class="performance-value">{proc.performance}%</div>
                    <div class="performance-sub">{proc.good_reps} / {proc.total_reps} good reps</div>
                </div>
                """, unsafe_allow_html=True)

                pct = min(int(proc.angle), 180) / 180 * 100 if proc.angle else 0
                progress_placeholder.markdown(f"""
                <div class="progress-card">
                    <div class="progress-label">
                        <span>Range of motion</span>
                        <span style="color:#0d1b3e;font-weight:600">{int(pct)}%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{pct:.0f}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                tip_placeholder.markdown(f"""
                <div class="tip-card">
                    💡 <strong>Tip:</strong> {tips[exercise_choice]}
                </div>
                """, unsafe_allow_html=True)

                time.sleep(0.1)

        else:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-card-label">📈 Rep Counter</div>
                <div class="stat-card-value">0</div>
                <div class="stat-card-sub">Total repetitions</div>
            </div>
            <div class="stat-row">
                <div class="stat-sm">
                    <div class="stat-sm-label">Stage</div>
                    <div class="stat-sm-val">—</div>
                </div>
                <div class="stat-sm">
                    <div class="stat-sm-label">Angle</div>
                    <div class="stat-sm-val">—°</div>
                </div>
            </div>
            <div class="feedback-card">
                💬 Start the webcam to see live stats
            </div>
            <div class="tip-card">
                💡 <strong>Tip:</strong> {tips[exercise_choice]}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        .webcam-header {
            background: linear-gradient(120deg, #0d1b3e 55%, #1a3a6b 100%);
            margin: -40px 0 20px 0;
            border-radius: 10px;
            padding: 36px;
            text-align: center;
        }
        .webcam-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            color: rgba(255,255,255,0.7);
            border-radius: 999px;
            padding: 5px 14px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 14px;
            font-family: 'Inter', sans-serif;
        }
        .live-dot {
            width: 7px;
            height: 7px;
            background: #ff4444;
            border-radius: 50%;
        }
        .webcam-header-title {
            font-family: 'Barlow Condensed', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            color: white;
            letter-spacing: 0.3px;
            line-height: 1;
            text-align: center;
            margin-bottom: 8px;
        }
        .webcam-header-sub {
            font-family: 'Inter', sans-serif;
            color: rgba(255,255,255,0.45);
            font-size: 0.85rem;
            text-align: center;
        }
        .webcam-pills {
            display: flex;
            gap: 8px;
            justify-content: center;
            margin-top: 16px;
        }
        .webcam-pill {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.6);
            border-radius: 999px;
            padding: 4px 14px;
            font-size: 0.7rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
        }

        /* ── Selectbox card ── */
        [data-testid="stSelectbox"] {
            background: white;
            border: 1.5px solid #dde3f5;
            border-radius: 14px;
            padding: 14px 16px 16px 16px;
            margin: 45px 0 0 0;
        }
        [data-testid="stSelectbox"] label {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            letter-spacing: 1.2px !important;
            text-transform: uppercase !important;
            color: #94a3b8 !important;
        }
        [data-testid="stSelectbox"] > div > div {
            background: #f0f4ff;
            border-radius: 8px !important;
            border: 1px solid #dde3f5 !important;
            color: #0d1b3e !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            margin-top: 6px;
        }

        /* ── Webcam card label ── */
        .webcam-card-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: #6b7a99;
            margin-bottom: 8px;
        }

        /* ── Stats title ── */
        .stats-title {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: #0d1b3e;
            margin: 45px 0 12px 0;
            background: white;
            border: 1.5px solid #dde3f5;
            border-radius: 14px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* ── Rep counter card ── */
        .stat-card {
            background: #f8faff;
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
        }
        .stat-card-label {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        .stat-card-value {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 2.4rem;
            font-weight: 800;
            color: #0d1b3e;
            line-height: 1;
        }
        .stat-card-sub {
            font-size: 0.72rem;
            color: #9ca3af;
            margin-top: 3px;
        }

        /* ── Stage + Angle row ── */
        .stat-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 10px;
        }
        .stat-sm {
            background: #f8faff;
            border-radius: 14px;
            padding: 12px 14px;
            font-family: 'Inter', sans-serif;
        }
        .stat-sm-label {
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        .stat-sm-val {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.4rem;
            font-weight: 800;
            color: #0d1b3e;
        }

        /* ── Feedback card ── */
        .feedback-card {
            border-left: 5px solid #0d1b3e;
            background: white;
            border-radius: 0 10px 10px 0;
            padding: 10px 14px;
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            color: #0d1b3e;
            margin-bottom: 10px;
            line-height: 1.5;
        }

        /* ── Progress card ── */
        .progress-card {
            background: white;
            border: 1px solid #dde3f5;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
        }
        .progress-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            font-weight: 600;
            color: #0d1b3e;
            margin-bottom: 8px;
        }
        .progress-track {
            background: #f0f4ff;
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 6px;
            background: linear-gradient(90deg, #0d1b3e, #1a3a6b);
            transition: width 0.3s ease;
        }

        /* ── Tip card ── */
        .tip-card {
            background: #f8faff;
            border-radius: 12px;
            padding: 12px 14px;
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #6b7a99;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .tip-card strong {
            color: #0d1b3e;
            font-weight: 700;
        }

        /* ── Hide default st.metric ── */
        [data-testid="stMetric"] { display: none !important; }

        hr { border-color: rgba(100,120,255,0.15) !important; }
        .quality-card {
            background: linear-gradient(135deg, #f8faff, #eef2ff);
            border-radius: 16px;
            padding: 18px;
            text-align: center;
            margin-bottom: 10px;
            border: 1px solid #dde3f5;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }

        .quality-label {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #9ca3af;
            margin-bottom: 6px;
            font-family: 'Inter', sans-serif;
        }

        .quality-value {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 4px;
        }

        .quality-sub {
            font-size: 0.7rem;
            color: #9ca3af;
            font-family: 'Inter', sans-serif;
        }
        .performance-card {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
        }

        .performance-label {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #16a34a;
            margin-bottom: 4px;
        }

        .performance-value {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #15803d;
        }

        .performance-sub {
            font-size: 0.72rem;
            color: #6b7280;
        }
        </style>
        """, unsafe_allow_html=True)
    
elif page == "Progress":

    TODAY     = datetime.today()
    TODAY_STR = TODAY.strftime("%Y-%m-%d")
    TODAY_STR_LOCAL = datetime.today().strftime("%Y-%m-%d")
    HOUR      = TODAY.hour

    if "session_log" not in st.session_state:
        if os.path.exists("session_log.json"):
            with open("session_log.json", "r") as f:
                st.session_state.session_log = json.load(f)
        else:
            st.session_state.session_log = {}

    if "prog_rest_days" not in st.session_state:
        if os.path.exists("rest_days.json"):
            with open("rest_days.json", "r") as f:
                st.session_state.prog_rest_days = set(json.load(f))
        else:
            st.session_state.prog_rest_days = set()
    if "prog_streak" not in st.session_state or "streak_updated" not in st.session_state:
        if os.path.exists("streak.json"):
            with open("streak.json", "r") as f:
                streak_data = json.load(f)
            st.session_state.prog_streak    = streak_data.get("streak", 0)
            st.session_state.streak_updated = streak_data.get("updated", None)
        else:
            st.session_state.prog_streak    = 0
            st.session_state.streak_updated = None
    if "goals_vals" not in st.session_state:
        if os.path.exists("goals_vals.json"):
            with open("goals_vals.json", "r") as f:
                st.session_state.goals_vals = json.load(f)
        else:
            st.session_state.goals_vals = {
                "steps": 0, "water": 0, "sleep": 0,
                "cardio": 0, "km": 0
            }
    if "weight_log" not in st.session_state:
        if os.path.exists("weight_log.json"):
            with open("weight_log.json", "r") as f:
                st.session_state.weight_log = json.load(f)
        else:
            st.session_state.weight_log = {}

    # Sync onboarding weight to today if today has no entry yet
    _onboard_weight = st.session_state.user_profile.get("weight", 0) if st.session_state.user_profile else 0
    if _onboard_weight and TODAY_STR not in st.session_state.weight_log:
        st.session_state.weight_log[TODAY_STR] = float(_onboard_weight)
        save_weight()

    if "custom_targets" not in st.session_state:
        if os.path.exists("custom_targets.json"):
            with open("custom_targets.json", "r") as f:
                st.session_state.custom_targets = json.load(f)
        else:
            st.session_state.custom_targets = {
                "steps": 10000, "water": 2.5, "sleep": 8.0,
                "weight": 75.0, "cardio": 30, "km": 5.0
            }
    if "selected_hist" not in st.session_state: st.session_state.selected_hist = TODAY_STR_LOCAL
    if "prog_split"     not in st.session_state: st.session_state.prog_split     = "Bro Split"
    if "prog_muscle"    not in st.session_state: st.session_state.prog_muscle    = None
    if "nut_selected_date" not in st.session_state: st.session_state.nut_selected_date = TODAY_STR
    if "goals_opt_on"   not in st.session_state: st.session_state.goals_opt_on   = {"km":False,"cardio":False}

    if "food_log" not in st.session_state:
        if os.path.exists("food_log.json"):
            with open("food_log.json", "r") as f:
                st.session_state.food_log = json.load(f)
        else:
            _td = datetime.today().strftime("%Y-%m-%d")
            st.session_state.food_log = {
                _td: {"breakfast": [], "lunch": [], "dinner": [], "snacks": []}
            }

    if TODAY_STR not in st.session_state.food_log:
        st.session_state.food_log[TODAY_STR] = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snacks": []
        }

    if "user_goals" not in st.session_state:
        if os.path.exists("user_goals.json"):
            with open("user_goals.json", "r") as f:
                st.session_state.user_goals = json.load(f)
        else:
            st.session_state.user_goals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    # ── Derived values that depend on session_state being initialized ──
    goals = st.session_state.user_goals

    data = st.session_state.food_log[TODAY_STR]

    _all_items = [x for mv in st.session_state.food_log[TODAY_STR].values() for x in mv]
    _total_cal = sum(x["cal"] for x in _all_items)

    total_protein = sum(item.get("protein", 0) for item in _all_items)
    total_carbs   = sum(item.get("carbs",   0) for item in _all_items)
    total_fat     = sum(item.get("fat",     0) for item in _all_items)

    cal_goal     = goals["calories"]
    protein_goal = goals["protein"]
    carbs_goal   = goals["carbs"]
    fat_goal     = goals["fat"]

    cal_left     = max(0, cal_goal     - _total_cal)
    protein_left = max(0, protein_goal - total_protein)
    carbs_left   = max(0, carbs_goal   - total_carbs)
    fat_left     = max(0, fat_goal     - total_fat)

    _cal_pct = min(100, round(_total_cal / goals["calories"] * 100)) if goals["calories"] else 0

    GOALS_TARGET = {"steps":10000,"water":2.5,"wtime":45,"sleep":8.0,"km":5.0,"cardio":30}

    def goal_pct(gid):
        return min(100, round(st.session_state.goals_vals.get(gid,0) / GOALS_TARGET[gid] * 100))

    active_ids = ["steps","water","wtime","sleep"] + [k for k,v in st.session_state.goals_opt_on.items() if v]
    done_count = sum(1 for g in active_ids if goal_pct(g) >= 100)

    cal_goal_met = _cal_pct >= 80
    total_sig    = len(active_ids) + 1
    done_sig     = done_count + (1 if cal_goal_met else 0)
    overall_pct  = round(done_sig / max(total_sig,1) * 100)

    WEEKDAYS    = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    days_active = 7 - len(st.session_state.prog_rest_days)

    if overall_pct >= 75:
        if st.session_state.streak_updated != TODAY_STR:
            st.session_state.prog_streak   += 1
            st.session_state.streak_updated = TODAY_STR
            save_streak()   # ← save karo
    else:
        if st.session_state.streak_updated == TODAY_STR:
            st.session_state.streak_updated = None
            save_streak() 

    if   5<=HOUR<12:  GREET,GEMOJI = "Good Morning","☀️"
    elif 12<=HOUR<17: GREET,GEMOJI = "Good Afternoon","⛅"
    elif 17<=HOUR<21: GREET,GEMOJI = "Good Evening","🌇"
    else:             GREET,GEMOJI = "Good Night","🌙"

    if overall_pct == 0:       motiv = "Let's get started — every rep counts! 💪"
    elif overall_pct < 30:     motiv = "Good start! Keep the momentum going."
    elif overall_pct < 50:     motiv = f"You're {overall_pct}% there — stay consistent!"
    elif overall_pct < 75:     motiv = f"More than halfway! Push harder, Athlete."
    elif overall_pct < 100:    motiv = f"So close! Just {100-overall_pct}% left to crush it 🔥"
    else:                      motiv = "Goal crushed! You're an absolute beast today 🏆"

    muscle_badge = ""
    if st.session_state.prog_muscle:
        muscle_badge = f'<div class="hero-muscle-badge">💪 {st.session_state.prog_muscle} Day</div>'

    if overall_pct >= 100:  bar_color = "#00e676"
    elif overall_pct >= 75: bar_color = "#00e676"
    elif overall_pct >= 50: bar_color = "#ffd600"
    else:                   bar_color = "#4f6ef7"

    goals_left = total_sig - done_sig

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

        [data-testid="stAppViewContainer"]>[data-testid="stMain"]{background:#f0f4ff!important}
        [data-testid="block-container"]{padding-top:1.2rem!important;padding-bottom:2rem!important}

        div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
            margin:0!important; padding:0!important; line-height:0!important;
        }

        .ph {
            background: linear-gradient(120deg, #0d1b3e 55%, #1a3a6b 100%);
            border-radius: 20px; padding: 28px 32px 24px;
            margin: -40px 0 10px 0; position: relative; overflow: hidden;
        }
        .ph-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px; position:relative; z-index:1; }
        .ph h2 { font-family:'Barlow Condensed',sans-serif; font-size:1.9rem; font-weight:800; color:#fff; margin:0; line-height:1.1; }
        .ph-date { font-family:'Inter',sans-serif; color:#7ea8d8; font-size:0.78rem; margin-top:3px; position:relative; z-index:1; }
        .ph-motiv { font-family:'Inter',sans-serif; color:rgba(255,255,255,0.6); font-size:0.8rem; margin-top:2px; position:relative; z-index:1; }
        .hero-muscle-badge { background:rgba(0,230,118,0.15); border:1px solid rgba(0,230,118,0.3); color:#00e676; border-radius:20px; padding:5px 14px; font-family:'Barlow Condensed',sans-serif; font-size:0.78rem; font-weight:800; letter-spacing:0.5px; white-space:nowrap; }
        .ph-pills { display:flex; gap:10px; margin-top:18px; position:relative; z-index:1; }
        .hp-pill { background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:10px 18px; text-align:center; min-width:80px; backdrop-filter:blur(4px); }
        .hp-pill .pn { font-family:'Barlow Condensed',sans-serif; font-size:1.8rem; font-weight:800; line-height:1; }
        .hp-pill .pl { font-size:0.6rem; color:rgba(255,255,255,0.45); text-transform:uppercase; letter-spacing:1px; margin-top:2px; }
        .ph-bar-wrap { margin-top:18px; position:relative; z-index:1; }
        .ph-bar-label { display:flex; justify-content:space-between; font-family:'Inter',sans-serif; font-size:0.7rem; color:rgba(255,255,255,0.45); margin-bottom:6px; }
        .ph-bar-track { height:6px; background:rgba(255,255,255,0.1); border-radius:99px; overflow:hidden; }
        .ph-bar-fill { height:100%; border-radius:99px; transition:width 0.5s ease; }
        .streak-banner { background:linear-gradient(90deg,#00c853,#00e676); border-radius:12px; padding:12px 18px; margin-bottom:14px; display:flex; align-items:center; gap:12px; }
        .streak-text { font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:800; color:#fff; }

        /* ── Secondary button ── */
        button[kind="secondary"] {
            background: white !important;
            border: 1.5px solid #dde3f5 !important;
            color: #0d1b3e !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        button[kind="secondary"]:hover {
            background: #f0f4ff !important;
            border-color: #b0bcef !important;
        }

        /* ── Primary button ── */
        button[kind="primary"] {
            background: #0d1b3e !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 700 !important;
        }
        button[kind="primary"]:hover {
            background: #1a3a6b !important;
        }
        .hist-card {
            background: white;
            border: 1.5px solid #dde3f5;
            border-radius: 14px;
            padding: 16px;
            margin-top: 12px;
            box-shadow: none;
        }
        .hist-card.empty {
            background: white;
            border: 1.5px solid #dde3f5;
            border-radius: 14px;
            padding: 16px;
            margin-top: 12px;
            box-shadow: none;
            opacity: 0.85;
        }
        .hist-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .hist-date {
            font-size: 0.75rem;
            color: #94a3b8;
        }
        .hist-main {
            font-size: 1rem;
            font-weight: 700;
            color: #0d1b3e;
            margin: 6px 0;
        }
        .hist-sub {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 2px;
        }
        .hist-tag {
            background: #f0f4ff;
            color: #0d1b3e;
            border: 1px solid #dde3f5;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 700;
        }
        .hist-tag.rest {
            background: #ffecec;
            color: #e53935;
            border: 1px solid #fecaca;
        }
        .hist-exercises {
            margin-top: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .ex-chip {
            background: #f0f4ff;
            border: 1.5px solid #dde3f5;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.7rem;
            color: #0d1b3e;
            font-weight: 600;
        }
        /* ── Toast ── */
        .app-toast {
            padding: 14px 18px;
            border-radius: 14px;
            margin-top: 14px;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: fadeSlide 0.35s ease;
        }
        .app-toast.success {
            background: #f0f4ff;
            border: 1.5px solid #b0bcef;
            color: #0d1b3e;
        }
        .app-toast.warning {
            background: #fffbeb;
            border: 1.5px solid #fcd34d;
            color: #b45309;
        }
        @keyframes fadeSlide {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0);   }
        }
        </style>
        """, unsafe_allow_html=True)

    if overall_pct >= 75 and st.session_state.streak_updated == TODAY_STR:
        st.markdown(f"""
        <div class="streak-banner">
            <span style="font-size:1.6rem">🔥</span>
            <div class="streak-text">Goal crushed! Streak updated to {st.session_state.prog_streak} days!</div>
        </div>
        """, unsafe_allow_html=True)

    goals_left_txt = f"{goals_left} goal{'s' if goals_left!=1 else ''} left" if goals_left > 0 else "All done! 🏆"

    st.markdown(f"""
    <div class="ph">
      <div class="ph-top">
        <div>
          <h2>{GEMOJI} {GREET}, {st.session_state.user_profile.get('name', 'Athlete')}!</h2>
          <div class="ph-date">{TODAY.strftime('%A, %b %d')}</div>
        </div>
        {muscle_badge}
      </div>
      <div class="ph-motiv">{motiv}</div>
      <div class="ph-pills">
        <div class="hp-pill">
          <div class="pn" style="color:#00e676">{st.session_state.prog_streak}</div>
          <div class="pl">🔥 Streak</div>
        </div>
        <div class="hp-pill">
          <div class="pn" style="color:{'#00e676' if overall_pct>=75 else '#ffd600'}">{overall_pct}%</div>
          <div class="pl">Today's Goal</div>
        </div>
        <div class="hp-pill">
          <div class="pn" style="color:#4f6ef7">{days_active}<span style="font-size:1rem">/7</span></div>
          <div class="pl">Active Days</div>
        </div>
      </div>
      <div class="ph-bar-wrap">
        <div class="ph-bar-label">
          <span>Daily Progress</span>
          <span>{goals_left_txt}</span>
        </div>
        <div class="ph-bar-track">
          <div class="ph-bar-fill" style="width:{overall_pct}%;background:{bar_color}"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION: Plan Today's Session ────────────────────────────────────────
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('''
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:4px; height:26px; background:#0d1b3e; border-radius:99px; flex-shrink:0;"></div>
        <div style="font-size:1.7rem; font-weight:800; color:#0d1b3e; font-family:\'Barlow Condensed\',sans-serif;">Plan Today\'s Session</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="display:inline-block; background:#0d1b3e; color:white; border-radius:6px; padding:4px 12px; font-size:0.68rem; font-weight:700; letter-spacing:0.5px; margin:14px 0 16px 0; font-family:\'Inter\',sans-serif;">Choose Your Split ⟩</div>', unsafe_allow_html=True)
    SPLITS = {
        "Bro Split":      ("🦾","1 muscle/day"),
        "Push/Pull/Legs": ("🗘","3-day rotation"),
        "Custom":         ("🖊","Mix muscles"),
    }
    sc1, sc2, sc3 = st.columns(3, gap="small")
    for col, (sp, (ico, desc)) in zip([sc1,sc2,sc3], SPLITS.items()):
        with col:
            is_active = st.session_state.prog_split == sp
            btn = st.button(f"{ico}\n\n{sp}\n{desc}", key=f"sp_{sp}", use_container_width=True)
            if btn:
                st.session_state.prog_split = sp
                st.session_state.prog_muscle = None
                st.rerun()

    st.markdown('<div style="display:inline-block; background:#0d1b3e; color:white; border-radius:6px; padding:4px 12px; font-size:0.68rem; font-weight:700; letter-spacing:0.5px; margin:0 0 16px 0; font-family:\'Inter\',sans-serif;">Rest Days &nbsp;<span style="font-weight:400;font-size:0.6rem;">(tap to toggle)</span></div>', unsafe_allow_html=True)

    rd_cols = st.columns(7, gap="small")
    for col, day in zip(rd_cols, WEEKDAYS):
        with col:
            active = day in st.session_state.prog_rest_days
            if st.button(day, key=f"rd_{day}", use_container_width=True, type="primary" if active else "secondary"):
                if active:
                    st.session_state.prog_rest_days.remove(day)
                else:
                    st.session_state.prog_rest_days.add(day)
                with open("rest_days.json", "w") as f:
                    json.dump(list(st.session_state.prog_rest_days), f)

                st.rerun()
    st.markdown('<div style="display:inline-block; background:#0d1b3e; color:white; border-radius:6px; padding:4px 12px; font-size:0.68rem; font-weight:700; letter-spacing:0.5px; margin:0 0 16px 0; font-family:\'Inter\',sans-serif;">Today\'s Muscles</div>', unsafe_allow_html=True)
    MUSCLES = ["Push","Pull","Legs"] if st.session_state.prog_split == "Push/Pull/Legs" else ["Chest","Back","Legs","Arms","Shoulders","Core"]
    mc_cols = st.columns(len(MUSCLES), gap="small")
    for col, m in zip(mc_cols, MUSCLES):
        with col:
            if st.button(m, key=f"mc_{m}", use_container_width=True):
                if st.session_state.prog_muscle == m:
                    st.session_state.prog_muscle = None
                    st.session_state.selected_exercises = []
                else:
                    st.session_state.prog_muscle = m
                    st.session_state.selected_exercises = []
                st.rerun()

    ml = st.session_state.prog_muscle
    bar_text = f"{ml} selected — ready to start!" if ml else "Select a muscle group above"

    EXERCISES = {
        "Chest": [
            "Bench Press", "Incline Dumbbell Press", "Chest Fly",
            "Decline Bench Press", "Cable Crossover", "Push Ups"
        ],
        "Back": [
            "Pull Ups", "Deadlift", "Lat Pulldown",
            "Seated Row", "T-Bar Row", "Single Arm Dumbbell Row"
        ],
        "Legs": [
            "Squats", "Leg Press", "Lunges",
            "Romanian Deadlift", "Leg Curl", "Calf Raises"
        ],
        "Arms": [
            "Bicep Curl", "Tricep Pushdown", "Hammer Curl",
            "Preacher Curl", "Skull Crushers", "Cable Curl"
        ],
        "Shoulders": [
            "Shoulder Press", "Lateral Raise", "Front Raise",
            "Arnold Press", "Rear Delt Fly", "Upright Row"
        ],
        "Core": [
            "Plank", "Crunches", "Leg Raise",
            "Russian Twist", "Mountain Climbers", "Bicycle Crunch"
        ],
        "Push": [
            "Bench Press", "Shoulder Press", "Tricep Dips",
            "Incline Bench Press", "Lateral Raise", "Cable Tricep Extension"
        ],
        "Pull": [
            "Pull Ups", "Barbell Row", "Bicep Curl",
            "Face Pull", "Hammer Curl", "Lat Pulldown"
        ]
    }

    st.markdown(f'<div class="sbar"><div class="sbar-text">{bar_text}</div></div>', unsafe_allow_html=True)

    if ml:
        ex_list = EXERCISES.get(ml, [])

        st.markdown("##### Select Exercises")

        if "selected_exercises" not in st.session_state:
            st.session_state.selected_exercises = []

        st.markdown('<div class="exercise-wrap">', unsafe_allow_html=True)

        cols = st.columns(3)

        for i, ex in enumerate(ex_list):
            col = cols[i % 3]

            with col:
                selected = ex in st.session_state.selected_exercises

                if st.button(
                    ex,
                    key=f"ex_{ml}_{ex}",
                    use_container_width=True,
                    type="primary" if selected else "secondary"
                ):
                    if selected:
                        st.session_state.selected_exercises.remove(ex)
                    else:
                        st.session_state.selected_exercises.append(ex)

                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✓ Log Session", key="log_sess", use_container_width=True, type="primary"):

        if not st.session_state.prog_muscle:
            st.session_state._log_msg = "⚠️ Select a muscle group first!"
            st.rerun()

        if st.session_state.selected_hist != TODAY_STR:
            st.session_state._log_msg = "⚠️ You can only log today's session"
            st.rerun()

        selected_muscle = st.session_state.prog_muscle

        # ✅ Save / overwrite today's session
        st.session_state.session_log[TODAY_STR] = {
            "split":  st.session_state.prog_split,
            "muscle": selected_muscle,
            "rest":   False,
            "exercises": st.session_state.get("selected_exercises", [])
        }

        save_log()  # ✅ ONLY this

        # reset UI
        st.session_state.selected_exercises = []
        st.session_state.prog_muscle = None

        st.session_state._log_msg = f"✅ {selected_muscle} session updated!"
        st.rerun()

    # ── SESSION HISTORY ───────────────────────────────────────────────────────
    st.markdown('<div style="display:inline-block; background:#0d1b3e; color:white; border-radius:6px; padding:4px 12px; font-size:0.68rem; font-weight:700; letter-spacing:0.5px; margin:0 0 16px 0; font-family:\'Inter\',sans-serif;">Session History</div>', unsafe_allow_html=True)
    TODAY = datetime.today()
    TODAY_STR_LOCAL = TODAY.strftime("%Y-%m-%d")
    DAYS = [TODAY - timedelta(days=i) for i in range(6, -1, -1)]
    cols = st.columns(7)

    for i, d in enumerate(DAYS):
        with cols[i]:
            dstr   = d.strftime("%Y-%m-%d")
            wd     = d.strftime("%a").upper()
            day    = d.day
            is_sel = dstr == st.session_state.selected_hist
            label = f"{wd}\n{day}\n{d.strftime('%b').upper()}"
            if st.button(label, key=f"hist_{dstr}", use_container_width=True, type="primary" if is_sel else "secondary"):
                st.session_state.selected_hist = dstr
                st.rerun()

    sel          = st.session_state.selected_hist
    sel_dt       = datetime.strptime(sel, "%Y-%m-%d")
    sel_lbl      = sel_dt.strftime("%A, %b %d")
    is_today_sel = sel == TODAY_STR_LOCAL

    if sel in st.session_state.session_log:
        entry = st.session_state.session_log[sel]
        is_rest_e = entry.get("rest", False)

        if is_rest_e:
            st.markdown(f"""
            <div class="hist-card rest">
                <div class="hist-top">
                    <div class="hist-date">🗓 {sel_lbl}</div>
                    <div class="hist-tag rest">Rest Day</div>
                </div>

                <div class="hist-main">😴 Recovery Day</div>
                <div class="hist-sub">Body recovering — no workout logged</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            ex_list = entry.get("exercises", [])

            ex_html = ""
            if ex_list:
                ex_html = "".join(
                    [f'<span class="ex-chip">{e}</span>' for e in ex_list]
                )

            st.markdown(f"""
            <div class="hist-card">
                <div class="hist-top">
                    <div class="hist-date">🗓 {sel_lbl}</div>
                    <div class="hist-tag">{entry['split']}</div>
                <div class="hist-main">{entry['muscle']} Day</div>
                <div class="hist-exercises">{ex_html}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="hist-card empty">
            <div class="hist-date">🗓 {sel_lbl}</div>
            <div class="hist-main">No Session</div>
            <div class="hist-sub">Nothing logged for this day</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if "_log_msg" in st.session_state:
        msg = st.session_state._log_msg

        if "✅" in msg:
            st.markdown(f'<div class="app-toast success">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="app-toast warning">{msg}</div>', unsafe_allow_html=True)

        del st.session_state._log_msg
     
    st.markdown('''
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:4px; height:26px; background:#0d1b3e; border-radius:99px; flex-shrink:0;"></div>
        <div style="font-size:1.7rem; font-weight:800; color:#0d1b3e; font-family:\'Barlow Condensed\',sans-serif;">Today's Stats</div>
    </div>
    ''', unsafe_allow_html=True)
    # FOOD CALORIE TRACKER
    FOOD_DB = {
        "Rice":           {"cal": 130,  "protein": 2.5, "carbs": 28.0, "fat": 0.3},
        "Dal":            {"cal": 116,  "protein": 9.0, "carbs": 20.0, "fat": 0.4},
        "Chicken Breast": {"cal": 165,  "protein": 31,  "carbs": 0.0,  "fat": 3.6},
        "Roti":           {"cal": 297,  "protein": 9.0, "carbs": 49.0, "fat": 3.0},
        "Milk":           {"cal": 42,   "protein": 3.4, "carbs": 5.0,  "fat": 1.0},
        "Egg":            {"cal": 155,  "protein": 13,  "carbs": 1.1,  "fat": 11.0},
        "Oats":           {"cal": 379,  "protein": 13,  "carbs": 68.0, "fat": 6.5},
        "Banana":         {"cal": 89,   "protein": 1.1, "carbs": 23.0, "fat": 0.3},
        "Brown Rice":     {"cal": 216,  "protein": 4.5, "carbs": 45.0, "fat": 1.8},
        "Paneer":         {"cal": 265,  "protein": 18,  "carbs": 1.2,  "fat": 20.0},
        "Sweet Potato":   {"cal": 86,   "protein": 1.6, "carbs": 20.0, "fat": 0.1},
        "Curd (Yogurt)":  {"cal": 61,   "protein": 3.5, "carbs": 4.7,  "fat": 3.3},
    }

    # ── donut helpers ─────────────────────────────────────────────────────────
    def _donut(pct, color, r, stroke, size):
        circ = round(2 * 3.14159 * r, 2)
        dash = round(circ * min(max(pct, 0), 100) / 100, 2)
        cx = cy = size // 2
        return (
            f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e8efff" stroke-width="{stroke}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-dasharray="{dash} {circ}" stroke-linecap="round"/></svg>'
        )
    def big_donut(pct, color):  return _donut(pct, color, r=34, stroke=7, size=88)
    def mini_donut(pct, color): return _donut(pct, color, r=23, stroke=6, size=60)

    # ── selected date ─────────────────────────────────────────────────────────
    sel_date = st.session_state.nut_selected_date

    if sel_date not in st.session_state.food_log:
        st.session_state.food_log[sel_date] = {
            "breakfast": [], "lunch": [], "dinner": [], "snacks": []
        }

    # ── compute totals for selected date ─────────────────────────────────────
    sel_items   = [x for mv in st.session_state.food_log[sel_date].values() for x in mv]
    sel_cal     = sum(x["cal"]     for x in sel_items)
    sel_protein = sum(x["protein"] for x in sel_items)
    sel_carbs   = sum(x["carbs"]   for x in sel_items)
    sel_fat     = sum(x["fat"]     for x in sel_items)

    # ── read goals fresh ──────────────────────────────────────────────────────
    _g        = st.session_state.user_goals
    _cal_goal  = float(_g["calories"]) if _g["calories"] else 0.0
    _pro_goal  = float(_g["protein"])  if _g["protein"]  else 0.0
    _carb_goal = float(_g["carbs"])    if _g["carbs"]    else 0.0
    _fat_goal  = float(_g["fat"])      if _g["fat"]      else 0.0

    _cal_left  = max(0.0, _cal_goal  - sel_cal)
    _pro_left  = max(0.0, _pro_goal  - sel_protein)
    _carb_left = max(0.0, _carb_goal - sel_carbs)
    _fat_left  = max(0.0, _fat_goal  - sel_fat)

    cal_ring  = min(100, round(sel_cal     / _cal_goal  * 100)) if _cal_goal  else 0
    pro_ring  = min(100, round(sel_protein / _pro_goal  * 100)) if _pro_goal  else 0
    carb_ring = min(100, round(sel_carbs   / _carb_goal * 100)) if _carb_goal else 0
    fat_ring  = min(100, round(sel_fat     / _fat_goal  * 100)) if _fat_goal  else 0

    st.markdown("""
    <style>

    /* Expander container */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        background: #ffffff;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 0px 1px;
    }

    /* Expander header */
    div[data-testid="stExpander"] > div:first-child {
        font-weight: 600;
        font-size: 0.85rem;
        color: #1e3a8a;
        background: #eff6ff;
        padding: 10px 14px;
    }
    details {
        border: none !important;
    }
    /* Card */
    .st-emotion-cache-1ne20ew {
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        background: #ffffff;
        min-height: 180px;
    }

    /* Title */
    div[data-testid="stVerticalBlock"] strong {
        font-size: 1rem;
        color: #1e3a8a;
    }

    /* Value */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: -10px 0 10px 0;
        font-size: 24px;
    }

    </style>
    """, unsafe_allow_html=True)


    TODAY_W     = datetime.today().strftime("%Y-%m-%d")
    YESTERDAY_W = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    today_weight     = float(st.session_state.weight_log.get(TODAY_W, 0.0))
    yesterday_weight = float(st.session_state.weight_log.get(YESTERDAY_W, 0.0))


    # ── Card Renderer ─────────────────────────────────────
    def render_card(col, emoji, label, unit, session_key, step, min_v, max_v, is_weight=False):

        target = float(st.session_state.custom_targets.get(session_key, 1))
        val    = float(today_weight if is_weight else st.session_state.goals_vals.get(session_key, 0))

        # 🔥 Trend logic FIXED
        if is_weight and today_weight and yesterday_weight:
            w_diff = round(today_weight - yesterday_weight, 1)

            if w_diff > 0:
                w_trend = "▲ +" + str(w_diff) + " kg"
            elif w_diff < 0:
                w_trend = "▼ " + str(w_diff) + " kg"
            else:
                w_trend = ""
        else:
            w_trend = ""

        with col:
            with st.container(border=True):

                st.markdown(f"**{emoji} {label}**")
                st.caption(f"Goal: {target} {unit}")

                st.markdown(f"### {val:.1f} {unit}")

                # ✅ Only show if exists (NO GAP ISSUE)
                if is_weight and w_trend:
                    st.caption(w_trend)

                # Buttons
                b1, b2, b3 = st.columns([1,2,1])

                with b1:
                    if st.button("del", key="minus_" + session_key):
                        if is_weight:
                            new = max(min_v, today_weight - step)
                            st.session_state.weight_log[TODAY_W] = new
                            save_weight()
                        else:
                            st.session_state.goals_vals[session_key] = max(min_v, val - step)
                            persist_progress()
                        st.rerun()

                with b2:
                    st.markdown(
                        f"<div style='text-align:center;font-size:18px;'>{val:.1f} {unit}</div>",
                        unsafe_allow_html=True
                    )

                with b3:
                    if st.button("add", key="plus_" + session_key):
                        if is_weight:
                            new = min(max_v, today_weight + step)
                            st.session_state.weight_log[TODAY_W] = new
                            save_weight()
                        else:
                            st.session_state.goals_vals[session_key] = min(max_v, val + step)
                            persist_progress()
                        st.rerun()

                # Expander
                with st.expander("Set Goal"):
                    new_target = st.number_input(
                        f"Set {label} goal",
                        value=float(target),
                        key="goal_" + session_key
                    )

                    if st.button("Save", key="save_" + session_key):
                        st.session_state.custom_targets[session_key] = new_target
                        save_custom_targets()
                        st.rerun()


    # ── Cards ─────────────────────────────────────────────
    all_cards = [
        ("🚶", "Steps",   "steps", "steps",  500,  0,   30000, False),
        ("💧", "Water",   "L",     "water",  0.25, 0,   10,    False),
        ("😴", "Sleep",   "hrs",   "sleep",  0.5,  0,   12,    False),
        ("⚖", "Weight",  "kg",    "weight", 0.1,   0,  200,   True),
        ("🏃", "Cardio",  "min",   "cardio", 5,    0,   180,   False),
        ("🏃🏻‍♂️‍➡️", "Running", "km",    "km",     0.5,  0,   50,    False),
    ]

    for i in range(0, len(all_cards), 3):
        cols = st.columns(3)
        for col, card in zip(cols, all_cards[i:i+3]):
            render_card(col, *card)

    # ── Nutrition Overview heading + date strip ───────────────────────────────
    st.markdown('<div class="nut-card">', unsafe_allow_html=True)
    st.markdown('''
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="width:4px; height:26px; background:#0d1b3e; border-radius:99px; flex-shrink:0;"></div>
        <div style="font-size:1.7rem; font-weight:800; color:#0d1b3e; font-family:\'Barlow Condensed\',sans-serif;">Track Food</div>
    </div>
    ''', unsafe_allow_html=True)
    
    strip_days = [datetime.today() - timedelta(days=i) for i in range(6, -1, -1)]
    date_cols  = st.columns(7, gap="small")
    for col, d in zip(date_cols, strip_days):
        dstr   = d.strftime("%Y-%m-%d")
        wd     = d.strftime("%a").upper()
        dn     = str(d.day)
        mn     = d.strftime("%b").upper()
        is_sel = dstr == st.session_state.nut_selected_date
        label  = f"{wd}\n{dn}\n{mn}"
        with col:
            if st.button(label, key=f"nut_date_{dstr}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.nut_selected_date = dstr
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── calorie + macro layout ────────────────────────────────────────────────
    left_col, right_col = st.columns([1.2, 1], gap="small")

    with left_col:
        for label, value, goal, color, icon, ring in [
            ("Protein left", f"{round(_pro_left)}g",  f"Goal: {round(_pro_goal)}g",  "#ef4444", "⚡", pro_ring),] :
            st.markdown(f"""
            <div style="
                background:white; border-radius:18px;
                padding:24px 16px; 
                box-shadow:0 4px 16px rgba(0,0,0,0.06);
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="
                            font-family:'Barlow Condensed',sans-serif;
                            font-size:1.7rem; font-weight:800;
                            color:#2563eb; line-height:1;
                        ">{round(_cal_left)}</div>
                        <div style="font-weight:700; color:#1e293b; font-size:1rem; margin-top:6px;">Calories left</div>
                        <div style="color:#94a3b8; font-size:0.8rem; margin-top:3px;">Goal: {round(_cal_goal)} kcal</div>
                    </div>
                    <div style="position:relative; width:88px; height:88px; flex-shrink:0;">
                        {big_donut(cal_ring, "#2563eb")}
                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.5rem;">🔥</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="
                    background:white; border-radius:14px; margin:10px 0 0 0;
                    padding:24px 16px; 
                    box-shadow:0 3px 10px rgba(0,0,0,0.05);
                    display:flex; justify-content:space-between; align-items:center;
                ">
                    <div>
                        <div style="
                            font-family:'Barlow Condensed',sans-serif;
                            font-size:1.7rem; font-weight:800;
                            color:{color}; line-height:1;
                        ">{value}</div>
                        <div style="font-weight:700; color:#1e293b; font-size:1rem; margin-top:6px;">{label}</div>
                        <div style="color:#94a3b8; font-size:0.8rem;">{goal}</div>
                    </div>
                    <div style="position:relative; width:88px; height:88px; flex-shrink:0;">
                        {mini_donut(ring, color)}
                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.5rem;">{icon}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with right_col:
        for label, value, goal, color, icon, ring in [
            ("Carbs left",   f"{round(_carb_left)}g", f"Goal: {round(_carb_goal)}g", "#f59e0b", "🌾", carb_ring),
            ("Fat left",     f"{round(_fat_left)}g",  f"Goal: {round(_fat_goal)}g",  "#3b82f6", "💧", fat_ring),
        ]:
            st.markdown(f"""
            <div style="
                background:white; border-radius:14px;
                padding:24px 16px; margin-bottom:10px;
                box-shadow:0 3px 10px rgba(0,0,0,0.05);
                display:flex; justify-content:space-between; align-items:center;
            ">
                <div>
                    <div style="
                        font-family:'Barlow Condensed',sans-serif;
                        font-size:1.7rem; font-weight:800;
                        color:{color}; line-height:1;
                    ">{value}</div>
                        <div style="font-weight:700; color:#1e293b; font-size:1rem; margin-top:6px;">{label}</div>
                        <div style="color:#94a3b8; font-size:0.8rem;">{goal}</div>
                </div>
                <div style="position:relative; width:88px; height:88px; flex-shrink:0;">
                    {mini_donut(ring, color)}
                    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.5rem;">{icon}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Set Goals ─────────────────────────────────────────────────────────────
    with st.expander("Set Your Nutrition Goals First", expanded=False):
        gc1, gc2 = st.columns(2)
        with gc1:
            new_cal = st.number_input("Calories Goal (kcal)", min_value=0, max_value=10000, step=50,
                                      value=int(st.session_state.user_goals["calories"]))
            new_pro = st.number_input("Protein Goal (g)",     min_value=0, max_value=500,   step=5,
                                      value=int(st.session_state.user_goals["protein"]))
        with gc2:
            new_carb = st.number_input("Carbs Goal (g)",      min_value=0, max_value=1000,  step=5,
                                       value=int(st.session_state.user_goals["carbs"]))
            new_fat  = st.number_input("Fat Goal (g)",        min_value=0, max_value=300,   step=5,
                                       value=int(st.session_state.user_goals["fat"]))
        if st.button("Save", type="primary", use_container_width=True):
            st.session_state.user_goals["calories"] = new_cal
            st.session_state.user_goals["protein"]  = new_pro
            st.session_state.user_goals["carbs"]    = new_carb
            st.session_state.user_goals["fat"]      = new_fat
            save_user_goals()
            st.session_state._food_msg = "✅ Goals saved!"
            st.rerun()

    # ── Meal Tracker ──────────────────────────────────────────────────────────
    if "active_meal_tab" not in st.session_state:
        st.session_state.active_meal_tab = "breakfast"
    if "food_search_query" not in st.session_state:
        st.session_state.food_search_query = ""

    MEAL_ICONS = {"breakfast":"⛅","lunch":"☀️","dinner":"🌃","snacks":"🍪"}
    sel_log  = st.session_state.food_log[sel_date]

    # ── 4 meal tabs ───────────────────────────────────────────────────────────
    tc1, tc2, tc3, tc4 = st.columns(4, gap="small")
    for col, meal_key in zip([tc1,tc2,tc3,tc4], ["breakfast","lunch","dinner","snacks"]):
        items  = sel_log.get(meal_key, [])
        m_cal  = round(sum(i["cal"] for i in items))
        icon   = MEAL_ICONS[meal_key]
        active = st.session_state.active_meal_tab == meal_key
        with col:
            if st.button(
                f"{icon} {meal_key.title()}\n{m_cal} kcal",
                key=f"meal_tab_{meal_key}",
                use_container_width=True,
                type="primary" if active else "secondary"
            ):
                st.session_state.active_meal_tab = meal_key
                st.session_state.food_search_query = ""
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    active_meal = st.session_state.active_meal_tab
    items       = sel_log.get(active_meal, [])

    # ── logged items with delete ──────────────────────────────────────────────
    if items and isinstance(items, list) and len(items) > 0:
        for idx, it in enumerate(items):
            name  = it.get("name", "Unknown")
            grams = round(it.get("grams", 0))
            cal   = round(it.get("cal", 0))
            pro   = round(it.get("protein", 0), 1)
            carbs = round(it.get("carbs", 0), 1)
            fat   = round(it.get("fat", 0), 1)

            # Each food item is its own expander
            with st.expander(f"{name}  ·  {grams}g  ·  {cal} kcal"):
                
                # Macro breakdown inside
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""
                    <div style="background:#fef2f2;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:1.3rem;font-weight:800;color:#ef4444;">{pro}g</div>
                        <div style="font-size:0.7rem;color:#94a3b8;">Protein</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div style="background:#fffbeb;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:1.3rem;font-weight:800;color:#f59e0b;">{carbs}g</div>
                        <div style="font-size:0.7rem;color:#94a3b8;">Carbs</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div style="background:#eff6ff;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:1.3rem;font-weight:800;color:#3b82f6;">{fat}g</div>
                        <div style="font-size:0.7rem;color:#94a3b8;">Fat</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Delete button inside expander
                if st.button(f"🗑", 
                            key=f"del_{sel_date}_{active_meal}_{idx}",
                            type="secondary",
                            use_container_width=True):
                    st.session_state.food_log[sel_date][active_meal].pop(idx)
                    save_food_log() 
                    st.rerun()

    # ── search box ────────────────────────────────────────────────────────────
    if f"clear_search_{active_meal}" not in st.session_state:
        st.session_state[f"clear_search_{active_meal}"] = False

    # Search input — key mein ek counter add karo jo add pe increment ho
    if f"search_counter_{active_meal}" not in st.session_state:
        st.session_state[f"search_counter_{active_meal}"] = 0

    counter = st.session_state[f"search_counter_{active_meal}"]

    query = st.text_input(
        "search",
        placeholder=f"Search food to add to {active_meal.title()}...",
        label_visibility="collapsed",
        key=f"food_search_input_{active_meal}_{counter}"  # counter change = input reset
    )
    # filter food db by query
    if query.strip():
        matches = [f for f in FOOD_DB.keys()
                   if query.strip().lower() in f.lower()]

        if not matches:
            st.markdown("""
            <div style="text-align:center;color:#94a3b8;padding:16px;
                        background:white;border-radius:12px;font-size:0.85rem;">
                No food found. Try a different name.
            </div>
            """, unsafe_allow_html=True)
        else:
            for food_name in matches:
                macro = FOOD_DB[food_name]
                st.markdown(f"""
                <div style="background:white;border-radius:12px;
                            padding:12px 16px;margin-bottom:6px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);
                            display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.88rem;font-weight:700;color:#1e293b;">{food_name}</div>
                        <div style="font-size:0.72rem;color:#94a3b8;">
                            per 100g &nbsp;·&nbsp;
                            🔥 {macro['cal']} kcal &nbsp;·&nbsp;
                            <span style="color:#ef4444;">{macro['protein']}g protein</span> &nbsp;·&nbsp;
                            <span style="color:#f59e0b;">{macro['carbs']}g carbs</span> &nbsp;·&nbsp;
                            <span style="color:#3b82f6;">{macro['fat']}g fat</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # grams input + add button for each result
                g1, g2 = st.columns([3, 1], gap="small")
                with g1:
                    grams_in = st.number_input(
                        f"Grams for {food_name}",
                        min_value=0.0, max_value=2000.0,
                        step=10.0, value=100.0,
                        key=f"grams_{active_meal}_{food_name}",
                        label_visibility="collapsed"
                    )
                with g2:
                    if st.button("＋ Add", key=f"add_{sel_date}_{active_meal}_{food_name}",
                            use_container_width=True, type="primary"):

                        base = FOOD_DB.get(food_name)
                        if base is None:
                            st.warning("Food not found.")
                            st.stop()

                        factor = grams_in / 100
                        st.session_state.food_log[sel_date][active_meal].append({
                            "name":    food_name,
                            "grams":   grams_in,
                            "cal":     round(base["cal"]     * factor, 2),
                            "protein": round(base["protein"] * factor, 2),
                            "carbs":   round(base["carbs"]   * factor, 2),
                            "fat":     round(base["fat"]     * factor, 2),
                        })

                        st.session_state[f"search_counter_{active_meal}"] += 1
                        st.session_state._food_msg = f"✅ {food_name} added!"
                        save_food_log()
                        st.rerun()

    # ── Daily Total ───────────────────────────────────────────────────────────
    all_today = [x for mv in sel_log.values() for x in mv]
    if all_today:
        tt_cal  = sum(i["cal"]     for i in all_today)
        tt_pro  = sum(i["protein"] for i in all_today)
        tt_carb = sum(i["carbs"]   for i in all_today)
        tt_fat  = sum(i["fat"]     for i in all_today)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#2563eb,#1d4ed8);
                    border-radius:16px;padding:16px 22px;margin-top:14px;
                    display:flex;justify-content:space-around;
                    color:white;text-align:center;">
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;">{round(tt_cal)}</div>
                <div style="font-size:0.7rem;opacity:0.75;">Total kcal</div>
            </div>
            <div style="width:1px;background:rgba(255,255,255,0.2);"></div>
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;color:#fca5a5;">{round(tt_pro,1)}g</div>
                <div style="font-size:0.7rem;opacity:0.75;">Protein</div>
            </div>
            <div style="width:1px;background:rgba(255,255,255,0.2);"></div>
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;color:#fde68a;">{round(tt_carb,1)}g</div>
                <div style="font-size:0.7rem;opacity:0.75;">Carbs</div>
            </div>
            <div style="width:1px;background:rgba(255,255,255,0.2);"></div>
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;color:#93c5fd;">{round(tt_fat,1)}g</div>
                <div style="font-size:0.7rem;opacity:0.75;">Fat</div>
            </div>
        </div>
        <div style="color:#94a3b8;font-size:0.68rem;margin-top:8px;text-align:center;">
            Note: Values are approximate and may vary.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* ── Search input ── */
    div[data-testid="stTextInput"] input::placeholder {
        color: #94a3b8;
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Inter', sans-serif !important;
        background-color: white !important;
        color: #0d1b3e !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #0d1b3e !important;
        box-shadow: none !important;
    }
    .st-emotion-cache-1py5frv input {
        background:white;
    }
    </style>
    """, unsafe_allow_html=True)     

elif page == "Music":
    music_page()

elif page == "Settings":   
    settings_page()



