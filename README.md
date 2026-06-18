# 🏋️ FitAI — AI-Based Smart Fitness Training and Tracking System

An AI-powered fitness trainer web app built with Python 
and Streamlit that tracks your workouts in real-time 
using your webcam.

## 🎯 Project Overview

FitAI is a complete fitness companion that uses computer 
vision to detect body pose, count reps automatically, 
and deliver live AI-powered voice feedback — all from 
your webcam. No gym equipment or wearables needed.

## ✨ Features

- **🎥 Live Rep Counter** — Real-time angle-based rep 
  counting using MediaPipe pose detection
- **🤖 AI Voice Feedback** — Personalized coaching via 
  Groq (Llama 3.1) based on your fitness level & goal
- **💪 8 Exercises Supported** — Bicep Curl, Pushups, 
  Squats, Shoulder Press, Tricep Dips, Lunges, 
  Lateral Raise, Plank
- **📚 Exercise Library** — Video demos for Chest, 
  Back & Legs with difficulty levels
- **📊 Progress Tracking** — Workout history, streaks, 
  rest days & session planning
- **🥗 Nutrition Tracker** — Food log with calorie & 
  macro tracking (Protein, Carbs, Fat)
- **🎵 Workout Music** — Upload & play your own songs
  while training
- **👤 User Profiles** — Personalized onboarding 
  with fitness goal & activity level

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Web framework |
| MediaPipe | Pose detection (33 landmarks) |
| OpenCV | Video & frame processing |
| Groq API (Llama 3.1) | AI voice feedback |
| pyttsx3 | Text-to-speech engine |

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/pranavsatalkar/FitAI-AI-Based-Smart-Fitness-Training-and-Tracking-System.git
cd FitAI

# Create virtual environment
python -m venv fitness_env
fitness_env\scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📂 Project Structure
FitAI/
├── .streamlit/
├── images/
├── music/
│   └── music.py
├── settings/
│   └── settings.py
├── .gitignore
├── README.md
├── app.py
└── requirements.txt


## 📌 Note

- Webcam required for live exercise tracking
- Add your own Groq API key in `app.py` to enable 
  AI voice feedback
- Video demos require exercise videos in `videos/` 
  folder (not included due to file size)

## 🎓 About

Built as a Final Year Project demonstrating the use 
of Computer Vision and Generative AI in real-world 
fitness applications.

---
Made with ❤️ | Python · Streamlit · MediaPipe · Groq AI