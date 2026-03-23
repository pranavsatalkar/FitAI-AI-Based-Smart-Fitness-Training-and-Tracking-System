import streamlit as st
import base64
from streamlit_option_menu import option_menu
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import mediapipe as mp
import numpy as np
import time

# ✅ MUST be first Streamlit call
st.set_page_config(
    page_title="AI Virtual Fitness Trainer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Welcome screen ────────────────────────────────────────────────────────────
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

if not st.session_state.welcomed:

    # ✅ Load image BEFORE st.markdown
    with open("images/welcome.jpg", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    # Hide sidebar on welcome screen
    st.markdown("""
    <style>
    [data-testid="stSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapse"] { display: none !important; }
    [data-testid="stAppViewContainer"]{ padding: 0 !important; overflow: hidden !important; }
    [data-testid="stMain"]            { padding: 0 !important; }
    [data-testid="block-container"]   { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"]   { gap: 0 !important; padding: 0 !important; }
    .element-container                { margin: 0 !important; padding: 0 !important; }
    html, body { overflow: hidden !important; height: 100vh !important; }
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
        border-radius:60px;
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
        color: #00e676;
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
        background-color: #002D72 !important;
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
        background: #1E88E5 !important;
        transform: translateY(-2px) !important;
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
                 width="42" height="42"
                 style="border-radius:10px;flex-shrink:0;object-fit:contain;">
            <div class="sidebar-brand">Train With FitAI</div>
        </div>
    """, unsafe_allow_html=True)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    nav_options = ["Home", "Exercises", "Progress", "Live Webcam", "Settings"]
    nav_index   = nav_options.index(st.session_state.current_page)

    selected = option_menu(
        menu_title=None,
        options=nav_options,
        icons=["houses", "activity", "bar-chart-fill", "camera-video", "gear"],
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
        background: rgba(0,230,118,0.15);
        color: #00e676;
        border: 1px solid rgba(0,230,118,0.3);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 16px;
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
    .hero-title span { color: #00e676; }
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
        background: linear-gradient(120deg, #5b6abf, #7c4abf);
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
        background-color: #002D72 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 32px !important;
        width: auto !important;
        transition: all 0.15s !important;
    }
    [data-testid="stButton"] > button:hover {
        background: #1E88E5 !important;
        transform: translateY(-1px) !important;
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
                <div class="num">3+</div>
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
        st.session_state.exercise_query = st.session_state.exercise_search
        st.session_state.exercise_screen = "results"

    def go_back():
        st.session_state.exercise_screen = "search"
        st.session_state.exercise_search = ""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Search page header ── */
    .exercise-search {
        background: #ffffff;
        border-radius: 20px;
        border: 1px solid #e4eaf5;
        padding: 40px 40px;
        text-align: center;
        margin:0 0 20px 0;
    }
    .search-badge {
        display: inline-block;
        background: #eef2ff;
        color: #4f6ef7;
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
        color: #0d1b3e;
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
        color: #6b7a99;
        margin-top: 10px;
    }

    /* ── Search input placeholder ── */
    div[data-testid="stTextInput"] input::placeholder {
        color: #aab4c8;
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Search input shape — keep your original rounded style ── */
    div[data-baseweb="input"] {
        border-top-left-radius: 18px !important;
        border-bottom-left-radius: 18px !important;
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #4f6ef7 !important;
        box-shadow: 0 0 0 3px rgba(79,110,247,0.1) !important;
    }

    /* ── Search arrow button ── */
    button[kind="secondary"] {
        background-color: #4f6ef7 !important;
        color: white !important;
        border-top-right-radius: 18px !important;
        border-bottom-right-radius: 18px !important;
        border-top-left-radius: 0 !important;
        border-bottom-left-radius: 0 !important;
        margin: 0 0 0 -10px;
        border: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #3d5ce0 !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }

    /* ── Back button ── */
    button[kind="primary"] {
        background-color: #4f6ef7 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        background-color: #3d5ce0 !important;
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

    /* ── Video placeholder ── */
    .video-placeholder {
        background: linear-gradient(135deg, #0d1b3e 0%, #1a3a6b 100%);
        border-radius: 12px 12px 0 0;
        height: 150px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        cursor: pointer;
    }
    .play-icon {
        width: 42px;
        height: 42px;
        background: rgba(255,255,255,0.12);
        border: 2px solid rgba(255,255,255,0.25);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        color: white;
    }
    .video-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        color: rgba(255,255,255,0.45);
        letter-spacing: 0.5px;
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
                placeholder="⛶ ⌕ │ Search Exercises",
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
                    "video": None,
                },
                {
                    "title": "Flat Bench Press",
                    "desc": "Compound movement that builds strength and size in chest, shoulders, and triceps.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Chest", "Barbell"],
                    "video": None,
                },
                {
                    "title": "Incline Bench Press",
                    "desc": "Targets the upper chest, shoulders and triceps for better chest definition.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Upper Chest", "Barbell"],
                    "video": None,
                },
                {
                    "title": "Decline Bench Press",
                    "desc": "Emphasizes the lower chest while minimizing shoulder involvement.",
                    "diff": "Advanced",
                    "diff_bg": "rgba(255,82,82,0.1)",
                    "diff_color": "#ff5252",
                    "tags": ["Lower Chest", "Barbell"],
                    "video": None,
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
                    "video": None,
                },
                {
                    "title": "Deadlift",
                    "desc": "Full body compound lift primarily targeting lower and upper back, glutes and hamstrings.",
                    "diff": "Advanced",
                    "diff_bg": "rgba(255,82,82,0.1)",
                    "diff_color": "#ff5252",
                    "tags": ["Back", "Barbell"],
                    "video": None,
                },
                {
                    "title": "Lat Pulldown",
                    "desc": "Machine exercise that targets the latissimus dorsi for a wider back.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Back", "Machine"],
                    "video": None,
                },
                {
                    "title": "Bent Over Row",
                    "desc": "Compound pulling movement targeting the entire back and rear delts.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Back", "Barbell"],
                    "video": None,
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
                    "video": None,
                },
                {
                    "title": "Lunges",
                    "desc": "Unilateral leg exercise targeting quads, hamstrings and glutes.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "No Equipment"],
                    "video": None,
                },
                {
                    "title": "Leg Press",
                    "desc": "Machine compound movement targeting quads, hamstrings and glutes safely.",
                    "diff": "Beginner",
                    "diff_bg": "rgba(0,200,83,0.1)",
                    "diff_color": "#00c853",
                    "tags": ["Legs", "Machine"],
                    "video": None,
                },
                {
                    "title": "Romanian Deadlift",
                    "desc": "Hip hinge movement primarily targeting hamstrings and glutes.",
                    "diff": "Intermediate",
                    "diff_bg": "rgba(255,170,0,0.1)",
                    "diff_color": "#ffaa00",
                    "tags": ["Legs", "Barbell"],
                    "video": None,
                },
            ],
        }

        if query in exercises_db:
            cols = st.columns(4, gap="small")
            for col, ex in zip(cols, exercises_db[query]):
                with col:
                    # Video or placeholder
                    if ex["video"]:
                        st.video(ex["video"])
                    else:
                        st.markdown("""
                        <div class="video-placeholder">
                            <div class="play-icon">▶</div>
                            <div class="video-label">Video coming soon</div>
                        </div>
                        """, unsafe_allow_html=True)

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


elif page == "Progress":
    pass

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
            "up_limit":   90,
            "down_limit": 160,
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
                    self.stage    = "DOWN"
                    self.feedback = "Keep going..."

                if self.angle < cfg["up_limit"] and self.stage == "DOWN":
                    self.stage    = "UP"
                    self.counter += 1
                    self.feedback = f"Rep {self.counter} done!"

                if self.stage is None:
                    self.feedback = "Get into position"

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
            <div class="webcam-header-title">Live Exercise Tracker</div>
            <div class="webcam-header-sub">Real-time pose detection & rep counting via webcam.</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([6, 4], gap="medium")

    with col1:
        if "last_exercise" not in st.session_state:
            st.session_state.last_exercise = "Bicep Curl"

        # ── Selectbox card ────────────────────────────────────────────────────
        exercise_choice = st.selectbox(
            "Select Exercise",
            list(EXERCISE_CONFIG.keys()),
            key="exercise_select"
        )

        tag_map = {
            "Bicep Curl": ["Arms", "Strength"],
            "Pushups":    ["Upper Body", "Strength"],
            "Squats":     ["Legs", "Power"],
        }
        pills_css = " | ".join(tag_map[exercise_choice])
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
            color: #5b6abf;
            background: rgba(100,120,255,0.1);
            border-radius: 20px;
            padding: 4px 12px;
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
        st.markdown('<div class="stats-title">Live Stats</div>',
                    unsafe_allow_html=True)

        tips = {
            "Bicep Curl": "Keep elbows locked at your sides. Full extension down, squeeze at the top.",
            "Pushups":    "Keep your core tight. Lower until elbows hit 90°, push fully back up.",
            "Squats":     "Feet shoulder-width apart. Drive knees out, hips below parallel for a full rep.",
        }

        if ctx.video_processor:
            rep_placeholder      = st.empty()
            stage_angle_ph       = st.empty()
            feedback_placeholder = st.empty()
            progress_placeholder = st.empty()
            tip_placeholder      = st.empty()

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

                pct = min(int(proc.angle), 180) / 180 * 100 if proc.angle else 0
                progress_placeholder.markdown(f"""
                <div class="progress-card">
                    <div class="progress-label">
                        <span>Range of motion</span>
                        <span style="color:#7c6abf;font-weight:600">{int(pct)}%</span>
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

    # ── Styles ────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Page header ── */
    .webcam-header { margin: -40px 0 20px 0; }
    .webcam-header-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 800;
        font-size: 2rem;
        color: #0d1b3e;
        letter-spacing: 0.3px;
        line-height: 1;
    }
    .webcam-header-sub {
        font-family: 'Inter', sans-serif;
        color: #6b7a99;
        font-size: 0.85rem;
        margin-top: 4px;
    }

    /* ── Selectbox card ── */
    [data-testid="stSelectbox"] {
        background: linear-gradient(135deg, #e8f4ff 0%, #f0e8ff 100%);
        border: 1px solid rgba(100,120,255,0.15);
        border-radius: 16px;
        padding: 14px 16px 16px 16px;
        margin:45px 0 0 0;
    }
    [data-testid="stSelectbox"] label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        color: #6b7a99 !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #ffffff !important;
        border: 1.5px solid rgba(100,120,255,0.2) !important;
        border-radius: 10px !important;
        color: #0d1b3e !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(100,120,255,0.08) !important;
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
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
        color: #0d1b3e;
        margin-bottom: 12px;
    }

    /* ── Rep counter card ── */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e4eaf5;
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
        background: #ffffff;
        border: 1px solid #e4eaf5;
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
        background: #f5f0ff;
        border-left: 3px solid #7c6abf;
        border-radius: 0 10px 10px 0;
        padding: 10px 14px;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #3d3d8f;
        margin-bottom: 10px;
        line-height: 1.5;
    }

    /* ── Progress card ── */
    .progress-card {
        background: #ffffff;
        border: 1px solid #e4eaf5;
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
        background: linear-gradient(90deg, #5b6abf, #7c4abf);
        transition: width 0.3s ease;
    }

    /* ── Tip card ── */
    .tip-card {
        background: #f4f7ff;
        border-radius: 12px;
        padding: 12px 14px;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #6b7a99;
        line-height: 1.6;
    }
    .tip-card strong {
        color: #0d1b3e;
        font-weight: 700;
    }

    /* ── Hide default st.metric ── */
    [data-testid="stMetric"] { display: none !important; }

    hr { border-color: rgba(100,120,255,0.15) !important; }
    </style>
    """, unsafe_allow_html=True)


elif page == "Settings":  
    pass