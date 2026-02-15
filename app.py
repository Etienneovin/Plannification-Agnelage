import streamlit as st
from datetime import timedelta, datetime
import pandas as pd

st.set_page_config(page_title="Agnel'Plan Pro", page_icon="🐑")

st.title("🐑 Agnel'Plan")
st.write("Personnalisez vos protocoles et générez votre planning.")

# --- 1. CONFIGURATION DE BASE ---
with st.sidebar:
    st.header("1. Paramètres du Lot")
    nom_lot = st.text_input("Nom du lot", value="Lot Printemps")
    date_debut_lutte = st.date_input("Début de lutte", datetime.now())
    nb_cycles = st.number_input("Nombre de cycles (16j)", min_value=1, value=2)
    
    st.divider()
    
    # --- 2. MENU OPTIONS PERSONNALISÉES ---
    st.header("2. Options du protocole")
    st.write("Réglez les dates par rapport à la mise bas :")
    
    d_echo = st.slider("Écho (jours après fin lutte)", 30, 90, 45)
    d_flush = st.slider("Flushing (jours avant mise bas)", 7, 40, 20)
    d_vaccin = st.slider("Vaccin / Rappel (jours avant mise bas)", 0, 60, 30)
    d_sevrage = st.slider("Sevrage (jours après mise bas)", 40, 120, 70)
    d_vente = st.slider("Vente (jours après mise bas)", 60, 200, 90)

# --- 3. CALCULS LOGIQUES ---
# Dates de lutte
duree_lutte = nb_cycles * 16
date_fin_lutte = date_debut_lutte + timedelta(days=duree_lutte)

# Dates clés basées sur les sliders
date_echo = date_fin_lutte + timedelta(days=d_echo)
date_mb_debut = date_debut_lutte + timedelta(days=147)
date_mb_fin = date_fin_lutte + timedelta(days=152)

date_flushing = date_mb_debut - timedelta(days=d_flush)
date_vaccin = date_mb_debut - timedelta(days=d_vaccin)
date_sevrage = date_mb_debut + timedelta(days=d_sevrage)
date_vente = date_mb_debut + timedelta(days=d_vente)

# --- 4. AFFICHAGE DES RÉSULTATS ---
st.subheader(f"Planning : {nom_lot}")

# Création d'un tableau propre pour l'affichage
data = [
    ["Lutte (Période)", f"Du {date_debut_lutte.strftime('%d/%m')} au {date_fin_lutte.strftime('%d/%m')}"],
    ["Échographie", date_echo.strftime('%d/%m/%y')],
    ["Vaccination", date_vaccin.strftime('%d/%m/%y')],
    ["Flushing", date_flushing.strftime('%d/%m/%y')],
    ["Mise bas (Période)", f"Du {date_mb_debut.strftime('%d/%m')} au {date_mb_fin.strftime('%d/%m')}"],
    ["Sevrage", date_sevrage.strftime('%d/%m/%y')],
    ["Vente", date_vente.strftime('%d/%m/%y')],
]
df_display = pd.DataFrame(data, columns=["Événement", "Date / Période"])
st.table(df_display)

# --- 5. LOGIQUE DU FICHIER ICS ---
def create_ics():
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AgnelPlan//FR"]
    
    # Fonction pour ajouter un événement
    def add_event(summary, start, end=None):
        ics.append("BEGIN:VEVENT")
        ics.append(f"SUMMARY:{summary} ({nom_lot})")
        ics.append(f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}")
        if end:
            ics.append(f"DTEND;VALUE=DATE:{(end + timedelta(days=1)).strftime('%Y%m%d')}")
        else:
            ics.append(f"DTEND;VALUE=DATE:{(start + timedelta(days=1)).strftime('%Y%m%d')}")
        ics.append("END:VEVENT")

    # Ajout des événements
    add_event("LUTTE", date_debut_lutte, date_fin_lutte)
    add_event("MISE BAS", date_mb_debut, date_mb_fin)
    add_event("Échographie", date_echo)
    add_event("Vaccination", date_vaccin)
    add_event("Flushing", date_flushing)
    add_event("Sevrage", date_sevrage)
    add_event("Vente agneaux", date_vente)
    
    ics.append("END:VCALENDAR")
    return "\n".join(ics)

# Bouton de téléchargement
st.download_button(
    label="📲 Exporter vers mon Agenda",
    data=create_ics(),
    file_name=f"AgnelPlan_{nom_lot}.ics",
    mime="text/calendar",
    use_container_width=True
)
