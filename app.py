import streamlit as st
from datetime import timedelta, datetime
import pandas as pd

# 1. CONFIGURATION & STYLE VINTAGE
st.set_page_config(page_title="Agnel'Plan", page_icon="🐑", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; }
    h1, h2, h3, p, span, label { color: #4A3728 !important; font-family: 'Georgia', serif; }
    .stButton>button { 
        background-color: #4A3728; color: #FDFBF7; border-radius: 4px; 
        border: 1px solid #4A3728; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #634a36; color: #FDFBF7; }
    div[data-baseweb="input"] { background-color: #FFF; border: 1px solid #D1C4B9; }
    .stDataFrame { border: 1px solid #4A3728; }
    </style>
    """, unsafe_allow_html=True)

# EN-TÊTE
col_a, col_b = st.columns([1, 5])
with col_a:
    st.write("# 🐑")
with col_b:
    st.title("Agnel'Plan")
    st.write("*Carnet de bergerie digital*")

# 2. SAISIE DU LOT
with st.container():
    c1, c2, c3 = st.columns([2, 2, 1])
    nom_lot = c1.text_input("Nom du lot", value="Lot 1")
    date_debut = c2.date_input("Début lutte", datetime.now())
    cycles = c3.number_input("Cycles", min_value=1, value=2)

# 3. OPTIONS & PERSONNALISATION
with st.expander("⚙️ Réglages & Événements personnalisés"):
    col_opt1, col_opt2 = st.columns(2)
    d_echo = col_opt1.number_input("Écho (J+ fin)", value=45)
    d_flush = col_opt1.number_input("Flushing (J- début MB)", value=20)
    d_sevrage = col_opt2.number_input("Sevrage (J+ début MB)", value=70)
    d_vente = col_opt2.number_input("Vente (J+ début MB)", value=90)
    
    st.divider()
    c_nom = st.text_input("Ajouter une note (ex: Tonte)")
    cx1, cx2, cx3 = st.columns([2,1,1])
    c_ref = cx1.selectbox("Réf.", ["Avant MB", "Après MB"])
    c_jours = cx2.number_input("Jours", value=10)
    add_btn = cx3.button("Ajouter")

# Gestion des événements personnalisés
if 'customs' not in st.session_state:
    st.session_state.customs = []
if add_btn and c_nom:
    st.session_state.customs.append({"nom": c_nom, "ref": c_ref, "jours": c_jours})

# 4. CALCULS
d_lutte = cycles * 16
date_fin_l = date_debut + timedelta(days=d_lutte)
date_mb_deb = date_debut + timedelta(days=147)
date_mb_fin = date_fin_l + timedelta(days=152)

# Préparation de la liste d'événements
plan = [
    {"label": "🚀 Lutte", "start": date_debut, "end": date_fin_l},
    {"label": "🩺 Échographie", "start": date_fin_l + timedelta(days=d_echo)},
    {"label": "🌾 Flushing", "start": date_mb_deb - timedelta(days=d_flush)},
    {"label": "✨ Mises bas", "start": date_mb_deb, "end": date_mb_fin},
    {"label": "🍼 Sevrage", "start": date_mb_deb + timedelta(days=d_sevrage)},
    {"label": "💰 Vente", "start": date_mb_deb + timedelta(days=d_vente)},
]

for ev in st.session_state.customs:
    d_ev = date_mb_deb - timedelta(days=ev['jours']) if ev['ref'] == "Avant MB" else date_mb_deb + timedelta(days=ev['jours'])
    plan.append({"label": f"⭐ {ev['nom']}", "start": d_ev})

# 5. AFFICHAGE STYLE ÉPURÉ
st.write("### 📅 Planning")
df_view = []
for p in plan:
    date_str = f"{p['start'].strftime('%d/%m/%Y')}"
    if 'end' in p:
        date_str = f"Du {p['start'].strftime('%d/%m')} au {p['end'].strftime('%d/%m/%Y')}"
    df_view.append({"Action": p['label'], "Date": date_str})

st.table(pd.DataFrame(df_view))

# 6. GÉNÉRATEUR DE FICHIER ICS
def create_ics():
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AgnelPlan//FR", "CALSCALE:GREGORIAN"]
    for p in plan:
        ics.append("BEGIN:VEVENT")
        ics.append(f"SUMMARY:{p['label']} ({nom_lot})")
        ics.append(f"DTSTART;VALUE=DATE:{p['start'].strftime('%Y%m%d')}")
        end_dt = p.get('end', p['start']) + timedelta(days=1)
        ics.append(f"DTEND;VALUE=DATE:{end_dt.strftime('%Y%m%d')}")
        ics.append("END:VEVENT")
    ics.append("END:VCALENDAR")
    return "\n".join(ics)

st.download_button(
    label="📲 Enregistrer dans l'agenda",
    data=create_ics(),
    file_name=f"AgnelPlan_{nom_lot}.ics",
    mime="text/calendar"
)

if st.session_state.customs:
    if st.button("Effacer les notes"):
        st.session_state.customs = []
        st.rerun()
