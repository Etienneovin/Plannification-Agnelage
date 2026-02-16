import streamlit as st
from datetime import timedelta, datetime
import pandas as pd

# Configuration de base
st.set_page_config(page_title="Agnel'Plan", page_icon="🐑")

# Style Vintage
st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; }
    h1, h2, h3, p, label { color: #4A3728 !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #4A3728; color: #FDFBF7; width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐑 Agnel'Plan")
st.write("*Carnet de bergerie*")

# --- SAISIE ---
with st.container():
    col1, col2 = st.columns(2)
    nom_lot = col1.text_input("Nom du lot", value="Lot 1")
    date_lutte = col2.date_input("Début lutte", datetime.now())
    cycles = st.slider("Nombre de cycles", 1, 4, 2)

# --- CALCULS ---
date_fin_l = date_lutte + timedelta(days=cycles * 16)
date_mb = date_lutte + timedelta(days=147)
date_mb_fin = date_fin_l + timedelta(days=152)
date_echo = date_fin_l + timedelta(days=45)
date_sevrage = date_mb + timedelta(days=70)

# --- TABLEAU ---
st.subheader("📅 Planning")
data = [
    {"Étape": "🚀 Lutte", "Période": f"Du {date_lutte.strftime('%d/%m')} au {date_fin_l.strftime('%d/%m')}"},
    {"Étape": "🩺 Écho", "Date": date_echo.strftime('%d/%m/%Y')},
    {"Étape": "✨ Mises bas", "Période": f"Du {date_mb.strftime('%d/%m')} au {date_mb_fin.strftime('%d/%m')}"},
    {"Étape": "🍼 Sevrage", "Date": date_sevrage.strftime('%d/%m/%Y')},
]
st.table(pd.DataFrame(data))

# --- EXPORT CALENDRIER ---
def create_ics():
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AgnelPlan//FR"]
    events = [
        ("Lutte", date_lutte, date_fin_l),
        ("Echo", date_echo, date_echo),
        ("Mise Bas", date_mb, date_mb_fin),
        ("Sevrage", date_sevrage, date_sevrage)
    ]
    for name, start, end in events:
        lines.append("BEGIN:VEVENT")
        lines.append(f"SUMMARY:{name} - {nom_lot}")
        lines.append(f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}")
        lines.append(f"DTEND;VALUE=DATE:{(end + timedelta(days=1)).strftime('%Y%m%d')}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

st.download_button("📲 Enregistrer dans l'agenda", data=create_ics(), file_name="planning.ics")
