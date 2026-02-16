
import streamlit as st
from datetime import timedelta, datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Agnel'Plan Pro", page_icon="🐑", layout="centered")

st.title("🐑 Agnel'Plan")
st.write("Planifiez vos lots et ajoutez vos propres étapes personnalisées.")

# --- 1. PARAMÈTRES DU LOT ---
st.subheader("📋 Configuration du Lot")
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        nom_lot = st.text_input("Nom du lot", value="Lot Printemps")
        date_debut_lutte = st.date_input("Date de début de lutte", datetime.now())
    with col2:
        nb_cycles = st.number_input("Nombre de cycles (16 jours/cycle)", min_value=1, value=2)
        st.caption(f"Durée totale de lutte : {nb_cycles * 16} jours")

# --- 2. RÉGLAGES STANDARDS ---
with st.expander("⚙️ Réglages des étapes classiques (jours)"):
    c1, c2 = st.columns(2)
    with c1:
        d_echo = st.number_input("Écho (J+ fin lutte)", value=45)
        d_sevrage = st.number_input("Sevrage (J+ début MB)", value=70)
    with c2:
        d_flush = st.number_input("Flushing (J- début MB)", value=20)
        d_vente = st.number_input("Vente (J+ début MB)", value=90)

# --- 3. ÉVÉNEMENTS PERSONNALISÉS ---
st.subheader("➕ Événements supplémentaires")
if 'custom_events' not in st.session_state:
    st.session_state.custom_events = []

with st.container(border=True):
    c_name = st.text_input("Nom de votre événement (ex: Tonte, Vermifuge...)")
    c_col1, c_col2, c_col3 = st.columns([2, 1, 1])
    with c_col1:
        c_ref = st.selectbox("Référence", ["Avant mise bas", "Après mise bas"])
    with c_col2:
        c_days = st.number_input("Jours", min_value=0, value=10)
    with c_col3:
        st.write("") # Espacement
        st.write("")
        if st.button("Ajouter"):
            if c_name:
                st.session_state.custom_events.append({"nom": c_name, "ref": c_ref, "jours": c_days})
                st.rerun()

# Affichage et suppression des événements personnalisés
if st.session_state.custom_events:
    for i, ev in enumerate(st.session_state.custom_events):
        st.info(f"**{ev['nom']}** : {ev['jours']} jours {ev['ref'].lower()}")
        if st.button(f"Supprimer {i}", key=f"del_{i}"):
            st.session_state.custom_events.pop(i)
            st.rerun()

# --- 4. CALCULS ---
duree_lutte = nb_cycles * 16
date_fin_lutte = date_debut_lutte + timedelta(days=duree_lutte)
date_mb_debut = date_debut_lutte + timedelta(days=147)
date_mb_fin = date_fin_lutte + timedelta(days=152)

# Événements standards
date_echo = date_fin_lutte + timedelta(days=d_echo)
date_flushing = date_mb_debut - timedelta(days=d_flush)
date_sevrage = date_mb_debut + timedelta(days=d_sevrage)
date_vente = date_mb_debut + timedelta(days=d_vente)

# Préparation du tableau final
planning_data = [
    {"Événement": "🚀 Période de Lutte", "Date": f"Du {date_debut_lutte.strftime('%d/%m/%Y')} au {date_fin_lutte.strftime('%d/%m/%Y')}", "obj": (date_debut_lutte, date_fin_lutte)},
    {"Événement": "🩺 Diagnostic gestation", "Date": date_echo.strftime('%d/%m/%Y'), "obj": date_echo},
    {"Événement": "🌾 Début Flushing", "Date": date_flushing.strftime('%d/%m/%Y'), "obj": date_flushing},
    {"Événement": "🐣 Période de Mise bas", "Date": f"Du {date_mb_debut.strftime('%d/%m/%Y')} au {date_mb_fin.strftime('%d/%m/%Y')}", "obj": (date_mb_debut, date_mb_fin)},
    {"Événement": "🍼 Sevrage", "Date": date_sevrage.strftime('%d/%m/%Y'), "obj": date_sevrage},
    {"Événement": "💰 Vente agneaux", "Date": date_vente.strftime('%d/%m/%Y'), "obj": date_vente},
]

# Ajout des personnalisés aux calculs
for ev in st.session_state.custom_events:
    if ev['ref'] == "Avant mise bas":
        d_ev = date_mb_debut - timedelta(days=ev['jours'])
    else:
        d_ev = date_mb_debut + timedelta(days=ev['jours'])
    planning_data.append({"Événement": f"⭐ {ev['nom']}", "Date": d_ev.strftime('%d/%m/%Y'), "obj": d_ev})

# --- 5. AFFICHAGE ET EXPORT ---
st.divider()
st.subheader(f"📅 Planning : {nom_lot}")
df_display = pd.DataFrame([{"Événement": x["Événement"], "Date": x["Date"]} for x in planning_data])
st.table(df_display)

def create_ics():
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AgnelPlan//FR", "CALSCALE:GREGORIAN"]
    for item in planning_data:
        ics.append("BEGIN:VEVENT")
        ics.append(f"SUMMARY:{item['Événement']} - {nom_lot}")
        if isinstance(item['obj'], tuple): # Si c'est une période (Lutte/MB)
            start, end = item['obj']
            ics.append(f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}")
            ics.append(f"DTEND;VALUE=DATE:{(end + timedelta(days=1)).strftime('%Y%m%d')}")
        else: # Si c'est une date unique
            ics.append(f"DTSTART;VALUE=DATE:{item['obj'].strftime('%Y%m%d')}")
            ics.append(f"DTEND;VALUE=DATE:{(item['obj'] + timedelta(days=1)).strftime('%Y%m%d')}")
        ics.append("END:VEVENT")
    ics.append("END:VCALENDAR")
    return "\n".join(ics)

st.download_button(
    label="📲 Exporter vers mon Agenda",
    data=create_ics(),
    file_name=f"Planning_{nom_lot}.ics",
    mime="text/calendar",
    use_container_width=True,
    type="primary"
)
