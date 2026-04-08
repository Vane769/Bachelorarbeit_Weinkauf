import streamlit as st
import pandas as pd
import random
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===============================
# MAPPINGS 
# ===============================

blue_wine_position_map = {
    "R_o.jpg": "oben Mitte",
    "R_u.jpg": "unten Mitte",
    "R_Ah.jpg": "Augenhöhe Mitte",
    "kR_o.jpg": "oben Mitte",
    "kR_u.jpg": "unten Mitte",
    "kR_Ah.jpg": "Augenhöhe Mitte"
}

condition_map = {
    "R_o.jpg": "Discount_High",
    "R_u.jpg": "Discount_Low",
    "R_Ah.jpg": "Discount_EyeLevel",

    "kR_o.jpg": "NoDiscount_High",
    "kR_u.jpg": "NoDiscount_Low",
    "kR_Ah.jpg": "NoDiscount_EyeLevel"
}

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

if "no_discount_reason" not in st.session_state:
    st.session_state.no_discount_reason = ""

# ===============================
# PAGE 0
# ===============================

if st.session_state.page == 0:
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

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
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

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
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )
    if st.button("⬅️ Zurück"):
        st.session_state.page = 1
        st.rerun()
    st.write("Stellen Sie sich vor, Sie sind in einem Supermarkt und erledigen Ihren Einkauf.")

    st.write("Während Sie durch den Laden gehen, kommen Sie an einem Weinregal vorbei.")

    st.write("Sie haben noch ein Restbudget von 10 CHF übrig.")
    st.write("Sie können das Geld entweder für den Kauf eines Weins verwenden oder es behalten.")

    st.write("Bitte schauen Sie sich die folgende Situation kurz an und treffen Sie eine spontane Entscheidung, so wie Sie es im Alltag tun würden.")

    images = [
        "R_o.jpg",     # Discount_High 
        "R_u.jpg",     # Discount_Low 
        "R_Ah.jpg",    # Discount_EyeLevel

        "kR_o.jpg",    # NoDiscount_High 
        "kR_u.jpg",  # NoDiscount_Low
        "kR_Ah.jpg"     # NoDiscount_EyeLevel 
    ]
    if "image" not in st.session_state:
        st.session_state.image = random.choice(images)

    st.image(st.session_state.image)

    st.write("Wie würden Sie sich in dieser Situation entscheiden? ")

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

    if st.button("Weiter", key="weiter_page2"):
        st.session_state.choice = choice

        blue_position = blue_wine_position_map[st.session_state.image]

        condition = condition_map[st.session_state.image]

        is_discount_condition = condition.startswith("Discount")

        chose_discount = choice == blue_position

        if is_discount_condition and not chose_discount and choice != "Ich kaufe keinen Wein":
            st.session_state.page = 25   # neue Seite
        else:
            st.session_state.page = 3

        st.rerun()
# ===============================
# PAGE 2.5 
# ===============================

elif st.session_state.page == 25:
    if st.button("⬅️ Zurück", key="back_page25"):
       st.session_state.page = 2
       st.rerun()
    st.write("Sie haben sich gegen das Sonderangebot entschieden.")
  

    reason = st.radio(
        "Was war der Hauptgrund dafür? *",
        [
            "Ich bevorzuge diese Flasche",
            "Die Qualität wirkt höher",
            "Der Preisunterschied ist mir egal",
            "Ich habe das Angebot nicht bemerkt",
            "Zufällige Entscheidung",
            "Andere Gründe"
        ]
    )

    # Textfeld nur wenn "Andere Gründe"
    other_text = ""
    if reason == "Andere Gründe":
        other_text = st.text_input("Bitte geben Sie den Grund an:")

    
    if st.button("Weiter", key="weiter_page25"):

        if reason == "Andere Gründe" and other_text == "":
            st.warning("Bitte geben Sie einen Grund ein.")
        else:
            if reason == "Andere Gründe":
                st.session_state.no_discount_reason = other_text
            else:
                st.session_state.no_discount_reason = reason

            st.session_state.page = 3
            st.rerun()

# ===============================
# PAGE 3
# ===============================

elif st.session_state.page == 3:
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )
    if st.button("⬅️ Zurück"):
        st.session_state.page = 2
        st.rerun()

    st.write("Die folgenden Aussagen beziehen sich auf Ihre Wahrnehmung des Angebots sowie auf Ihren Entscheidungsprozess. "
         "Bitte geben Sie an, inwieweit Sie den Aussagen zustimmen.")
    
    show_scale_legend()

    with st.form("mechanisms_form"):

        deal1 = st.radio("Das Angebot wirkt attraktiv", list(range(1,6)), horizontal=True)
        deal2 = st.radio("Ich habe das Gefühl, Geld zu sparen", list(range(1,6)), horizontal=True)

        ease = st.radio("Die Entscheidung fiel mir leicht", list(range(1,6)), horizontal=True)
        quality = st.radio("Der Wein wirkt hochwertig", list(range(1,6)), horizontal=True)

        submitted = st.form_submit_button("Weiter")

        if submitted:
            st.session_state.data_mech = {
                "deal1": deal1,
                "deal2": deal2,
                "ease": ease,
                "quality": quality
            }
            st.session_state.page = 4
            st.rerun()

# ===============================
# PAGE 4
# ===============================

elif st.session_state.page == 4:
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )
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
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

    if st.button("⬅️ Zurück"):
       st.session_state.page = 4
       st.rerun()

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
# PAGE 6 
# ===============================

elif st.session_state.page == 6:
    st.markdown(
        """
        <script>
            window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )
    if st.button("⬅️ Zurück"):
        st.session_state.page = 5
        st.rerun()

    age = st.number_input("Alter:", 18, 100)
    gender = st.radio("Geschlecht:", ["Männlich", "Weiblich", "Keine Angabe"])

    st.divider()
    st.write('')
    st.write("🎁 Verlosung (optional)")
    st.write(
    "Unter allen Teilnehmenden wird ein Gewinn verlost. "
    "Je nach Ihrer Auswahl handelt es sich dabei entweder um einen Wein oder den entsprechenden Geldbetrag."
    )
    st.write("Wenn Sie an der Verlosung teilnehmen möchten, können Sie hier freiwillig Ihre E-Mail-Adresse angeben.*")
   
    email = st.text_input("E-Mail (optional)")
    st.caption("*Die E-Mail-Adresse wird ausschliesslich für die Durchführung der Verlosung verwendet und nicht mit Ihren Antworten verknüpft.")

    if st.button("Absenden", key="absenden_button"):

        existing_data = sheet_data.get_all_values()
        participant_id = len(existing_data)
        no_discount_reason = st.session_state.no_discount_reason

        condition_map = {
            # DISCOUNT
            "R_o.jpg": "Discount_High",
            "R_u.jpg": "Discount_Low",
            "R_Ah.jpg": "Discount_EyeLevel",

            # NO DISCOUNT
            "kR_o.jpg": "NoDiscount_High",
            "kR_u.jpg": "NoDiscount_Low",
            "kR_Ah.jpg": "NoDiscount_EyeLevel"
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
        sheet_reasons.append_row([
            participant_id,
            condition,
            st.session_state.choice,
            st.session_state.explanation,
            st.session_state.no_discount_reason,
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