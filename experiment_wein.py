import streamlit as st
import pandas as pd
import uuid
import random
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===============================
# GOOGLE SHEETS VERBINDUNG
# ===============================

@st.cache_resource
def get_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # Streamlit Cloud (Secrets)
        from streamlit import secrets
        creds_dict = secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    except Exception:
        # Lokal (JSON Datei)
        creds = ServiceAccountCredentials.from_json_keyfile_name(
        "ba-experiment-daten.json", scope
        )
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1v7zb6xaQdXWTT9nefbG5Sq2EL_YirxP3XIs-yPvDv7Q")

    return (
        sheet.worksheet("data"),
        sheet.worksheet("reasons"),
        sheet.worksheet("emails")
    )


sheet_data, sheet_reasons, sheet_emails = get_sheets()

# ===============================
# UI START
# ===============================

st.title("Studie zum Entscheidungsverhalten beim (W)einkauf 🍷")

def show_scale_legend():
    st.caption("1 = stimme überhaupt nicht zu | 3 = neutral | 5 = stimme voll zu")

# ===============================
# SESSION STATE
# ===============================

if "page" not in st.session_state:
    st.session_state.page = 0

# ===============================
# PAGE 0
# ===============================

if st.session_state.page == 0:

    st.write("Bitte bestätigen Sie die folgenden Punkte, bevor Sie fortfahren:")

    age_check = st.checkbox("Ich bin mindestens 18 Jahre alt")
    consent = st.checkbox("Ich stimme der Teilnahme zu")

    if st.button("Weiter") and age_check and consent:
        st.session_state.page = 1
        st.rerun()

# ===============================
# PAGE 1
# ===============================

elif st.session_state.page == 1:

    if st.button("⬅️ Zurück"):
        st.session_state.page = 0
        st.rerun()

    with st.form("screening_form"):
        st.write("Haben Sie in den letzten 12 Monaten Wein gekauft?")
        bought = st.radio("", ["Ja", "Nein"])

        submitted = st.form_submit_button("Weiter")

        if submitted:
            if bought == "Nein":
                st.session_state.page = 99
            else:
                st.session_state.page = 2
            st.rerun()

# ===============================
# PAGE 2
# ===============================

elif st.session_state.page == 2:

    if st.button("⬅️ Zurück"):
        st.session_state.page = 1
        st.rerun()

    st.write("Stellen Sie sich vor, Sie sind in einem Supermarkt und erledigen Ihren Einkauf.")
    st.write("Sie haben für Ihren Einkauf ein Budget von 20 CHF. Davon haben Sie bereits 10 CHF ausgegeben, 10 CHF verbleiben.")
    st.write("Beim Vorbeigehen am Weinregal schauen Sie sich die Auswahl an.")

    images = [
        "kR_nAh.jpg",
        "kR_Ah.jpg",
        "R_nAh.jpg",
        "R_Ah.jpg"
    ]

    if "image" not in st.session_state:
        st.session_state.image = random.choice(images)

    st.image(st.session_state.image)

    st.write("Sie können das Geld entweder für den Kauf eines Weins verwenden oder es behalten.")
    st.write("Wie würden Sie sich in dieser Situation entscheiden?")
    st.write("Bitte treffen Sie eine spontane Entscheidung.")

    st.markdown("**Bitte wählen Sie eine Option <span style='color:red'>*</span>:**", unsafe_allow_html=True)

    choice = st.radio(
        "Ich nehme die Flasche:",
        [
            "oben links", "oben Mitte", "oben rechts",
            "Augenhöhe links", "Augenhöhe Mitte", "Augenhöhe rechts",
            "unten links", "unten Mitte", "unten rechts",
            "Ich kaufe keinen Wein"
        ]
    )

    st.session_state.explanation = st.text_input("Was war der Hauptgrund für Ihre Entscheidung? (optional)")
    st.caption(
        "*Am Ende der Umfrage wird unter allen Teilnehmenden ein Gewinn verlost. "
        "Je nach Ihrer Auswahl handelt es sich dabei entweder um einen Wein oder den entsprechenden Geldbetrag."
    )

    if st.button("Weiter"):
        st.session_state.choice = choice
        st.session_state.page = 3
        st.rerun()

# ===============================
# PAGE 3
# ===============================

elif st.session_state.page == 3:

    if st.button("⬅️ Zurück"):
        st.session_state.page = 2
        st.rerun()

    show_scale_legend()

    with st.form("mechanisms_form"):

        deal1 = st.radio("Das Angebot wirkt attraktiv", list(range(1,6)), horizontal=True)
        deal2 = st.radio("Ich habe das Gefühl, Geld zu sparen", list(range(1,6)), horizontal=True)

        impuls1 = st.radio("Ich hatte spontan Lust diesen Wein zu kaufen", list(range(1,6)), horizontal=True)
        impuls2 = st.radio("Meine Entscheidung war eher spontan als geplant", list(range(1,6)), horizontal=True)

        ease = st.radio("Die Entscheidung fiel mir leicht", list(range(1,6)), horizontal=True)
        quality = st.radio("Der Wein wirkt hochwertig", list(range(1,6)), horizontal=True)

        submitted = st.form_submit_button("Weiter")

        if submitted:
            st.session_state.data_mech = {
                "deal1": deal1,
                "deal2": deal2,
                "impuls1": impuls1,
                "impuls2": impuls2,
                "ease": ease,
                "quality": quality
            }
            st.session_state.page = 4
            st.rerun()

# ===============================
# PAGE 4
# ===============================

elif st.session_state.page == 4:

    with st.form("check_form"):

        discount = st.radio("Haben Sie einen Rabatt erkannt?", ["Ja", "Nein", "Unsicher"])
        position = st.radio("Falls ja, wo war der Wein positioniert?", ["Oben", "Augenhöhe", "Unten", "Weiss nicht", "Keinen Rabatt erkannt"])

        submitted = st.form_submit_button("Weiter")

        if submitted:
            st.session_state.data_check = {
                "discount": discount,
                "position": position
            }
            st.session_state.page = 5
            st.rerun()

# ===============================
# PAGE 5
# ===============================

elif st.session_state.page == 5:

    show_scale_legend()

    with st.form("control_form"):

        involvement1 = st.radio("Ich interessiere mich für Wein", list(range(1,6)), horizontal=True)
        involvement2 = st.radio("Ich kenne mich mit Wein aus", list(range(1,6)), horizontal=True)

        price_sens = st.radio("Ich achte auf den Preis", list(range(1,6)), horizontal=True)

        frequency = st.radio(
            "Wie oft kaufen Sie Wein?",
            ["Selten", "1x/Monat", "2–3x/Monat", "Wöchentlich"]
        )

        submitted = st.form_submit_button("Weiter")

        if submitted:
            st.session_state.data_control = {
                "involvement1": involvement1,
                "involvement2": involvement2,
                "price_sens": price_sens,
                "frequency": frequency
            }
            st.session_state.page = 6
            st.rerun()

# ===============================
# PAGE 6 (ABSENDEN)
# ===============================

elif st.session_state.page == 6:

    age = st.number_input("Alter", 18, 100)
    gender = st.radio("Geschlecht", ["Männlich", "Weiblich", "Keine Angabe"])

    st.write('')
    st.write("🎁 Verlosung (optional)")
    st.write("Wenn Sie an der Verlosung teilnehmen möchten, können Sie hier freiwillig Ihre E-Mail-Adresse angeben.")
    st.write("Die E-Mail-Adresse wird ausschließlich für die Durchführung der Verlosung verwendet und nicht mit Ihren Antworten verknüpft.")
    email = st.text_input("E-Mail (optional)")

    if st.button("Absenden"):

        participant_id = str(uuid.uuid4())

        condition_map = {
            "kR_nAh.jpg": "NoDiscount_Low",
            "kR_Ah.jpg": "NoDiscount_High",
            "R_nAh.jpg": "Discount_Low",
            "R_Ah.jpg": "Discount_High"
        }

        condition = condition_map[st.session_state.image]

        data = {
            "participant_id": participant_id,
            "image": st.session_state.image,
            "condition": condition,
            "choice": st.session_state.choice,
            "gender": gender,
            "age": age,
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

        data.update(st.session_state.data_mech)
        data.update(st.session_state.data_check)
        data.update(st.session_state.data_control)

        # MAIN DATA
        sheet_data.append_row([
             participant_id,
             st.session_state.image,
             condition,
             0 if st.session_state.choice == "Ich kaufe keinen Wein" else 1,
             st.session_state.choice,

             st.session_state.data_mech["deal1"],
             st.session_state.data_mech["deal2"],
             st.session_state.data_mech["impuls1"],
             st.session_state.data_mech["impuls2"],
             st.session_state.data_mech["ease"],
             st.session_state.data_mech["quality"],

             st.session_state.data_check["discount"],
             st.session_state.data_check["position"],

             st.session_state.data_control["involvement1"],
             st.session_state.data_control["involvement2"],
             st.session_state.data_control["price_sens"],
             st.session_state.data_control["frequency"],

             gender,
             age,
             datetime.now().strftime("%d.%m.%Y %H:%M")
         ], value_input_option="RAW")

        # REASONS
        if st.session_state.explanation != "":
            sheet_reasons.append_row([
            participant_id,
            condition,
            st.session_state.choice,
            st.session_state.explanation,
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ], value_input_option="RAW")

        # EMAIL
        if email != "":
           sheet_emails.append_row([
           participant_id,
           email,
           0 if st.session_state.choice == "Ich kaufe keinen Wein" else 1,
           st.session_state.choice,
           datetime.now().strftime("%d.%m.%Y %H:%M")
       ], value_input_option="RAW")
        st.session_state.page = 7
        st.rerun()

# ===============================
# END
# ===============================

elif st.session_state.page == 7:
    st.write("Vielen Dank für Ihre Teilnahme! 🙏")

elif st.session_state.page == 99:
    st.write("Diese Studie richtet sich an Wein-Käufer.")