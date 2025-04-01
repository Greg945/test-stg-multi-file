import streamlit as st
from deepgramcomp import deepgramcomp
import streamlit.components.v1 as components
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, Part
import random
import json
import os
from threading import Timer
import csv
import datetime
import time
import PIL 
import io


client = genai.Client(api_key="AIzaSyA3iQXk6-M5XQhzLIMO3SfEAKDPRunTHP8")

google_search_tool = Tool(google_search=GoogleSearch())


if 'search' not in st.session_state:
    st.session_state.search = False


if "context" not in st.session_state:
    st.session_state.context = []


DEFAULT_LANGUAGE = "de-DE"

# Systemanweisung für Gemini
SYS_INSTRUCT = ('Du bist ein mithörender Assistent in einem Klassenzimmer. Wenn du eine Frage hörst, beantworte sie bitte normal. '
                'Wenn es keine Frage ist, antworte nur mit "Ignoriert". Außerdem bekommst du immer den Konversationsverlauf, '
                'den du nur benutzt, falls du Informationen daraus zur Beantwortung der Frage brauchst.')


def lade_stundenplan(datei="stundenplan.csv"):
    stundenplan = []
    with open(datei, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = datetime.datetime.strptime(row["Start"], "%H:%M").time()
            ende = datetime.datetime.strptime(row["Ende"], "%H:%M").time()
            stundenplan.append({"Start": start, "Ende": ende, "Fach": row["Fach"], "Tag": row["Tag"]})
    return stundenplan

def aktuelles_fach():
    jetzt = datetime.datetime.now()
    aktueller_tag = jetzt.strftime("%A")
    aktuelle_zeit = jetzt.time()
    for eintrag in st.session_state.stundenplan:
        if eintrag["Tag"] == aktueller_tag and eintrag["Start"] <= aktuelle_zeit < eintrag["Ende"]:
            return eintrag["Fach"]
    return ""

if "stundenplan" not in st.session_state:
    st.session_state.stundenplan = lade_stundenplan()

def save_chat_history(context):
    print("week: ", datetime.date.today().isocalendar().week , " year: ", datetime.date.today().year)
    week_dir = "history/" + str(datetime.date.today().isocalendar().week)
    CHAT_FILE = week_dir + "/chat_history" + aktuelles_fach() + str(datetime.date.today()) + ".json"
    
    try:
        # Erstelle den history-Ordner, falls er nicht existiert
        if not os.path.exists("history"):
            os.makedirs("history")
            
        # Erstelle den Wochen-Ordner, falls er nicht existiert
        if not os.path.exists(week_dir):
            os.makedirs(week_dir)
            
        # Erstelle oder aktualisiere die JSON-Datei
        with open(CHAT_FILE, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        st.error(f"Fehler beim Speichern des Chat-Verlaufs: {e}")

# def load_chat_history():
#     try:
#         if os.path.exists(CHAT_FILE):
#             with open(CHAT_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#     except Exception as e:
#         st.error(f"Fehler beim Laden des Chat-Verlaufs: {e}")
#     return [{"role": "user", "content": "hallo"}]  # Standardwert falls keine Historie existiert

# def load_chat_history():
#     try:
#         with open(CHAT_FILE, "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []

# def save_chat_history(chat_history):
#     with open(CHAT_FILE, "w") as f:
#         json.dump(chat_history, f)



def gemini_request(text, type="speech", file=None):
    context = st.session_state.context
    search_enabled = st.session_state.get("search", False)
    try:
        if type == "speech":
            content_parts = f'Konversations Verlauf:"{context}" Das hier ist das gehörte im Klassenraum: {text}'
        elif type == "custom":
            content_parts = f'Konversations Verlauf:"{context}" User eingabe: "{text}"'
        elif type == "file":
            for image in file:
                buffer = io.BytesIO()
                PIL.Image.open(image).save(buffer, format="JPEG") 
                image_input = PIL.Image.open(buffer)
                content_parts = [f'Konversations Verlauf:"{context}" User eingabe: "{text}"', image_input]
        else:
             # Fallback oder Fehlerbehandlung, falls 'type' ungültig ist
             st.error(f"Unbekannter Anfragetyp: {type}")
             return "Interner Fehler: Unbekannter Anfragetyp."
        
        if not content_parts:
             st.warning("Kein Inhalt zum Senden an die API.")
             return "Kein Inhalt zum Senden."

        response = client.models.generate_content( #######?????? client.gen... stat client.models.gen....
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=SYS_INSTRUCT if type == "speech" else "Du bist ein Assistent in einem Klassenzimmer. Antworte auf die Frage.",
                tools=[google_search_tool] if search_enabled else [],
                # response_modalities=["TEXT"]
            ),
            contents = content_parts,
        )
        response_text = response.text.strip()
    except Exception as e:
        response_text = f"Fehler bei der API-Anfrage: {e}"
        st.error(response_text)
        # Optional: Mehr Details loggen für Debugging
        import traceback
        print(traceback.format_exc())

    st.session_state.context.append({"user": text, "assistant": response_text})

    save_chat_history(st.session_state.context)
    print('Apicall for:', text)
    print('Response:', response_text)
    return response_text




def lang_switch():
    language_codes = {"Deutsch": "de-DE", "Englisch": "en-GB", "Französisch": "fr-FR"}
    if st.session_state.sprache != None:
        st.session_state.language_code = language_codes.get(st.session_state.sprache, DEFAULT_LANGUAGE)
    else:
        st.session_state.language_code = language_codes.get(aktuelles_fach(), DEFAULT_LANGUAGE)



##################################  UI  #########################################



settings = st.Page("seiten/settings.py", title="Settings", icon=":material/settings:")
photo = st.Page("seiten/settings.py", title="Photo", icon=":material/camera:")
stg = st.Page("seiten/stg.py", title="STG", icon=":material/camera:")


pg = st.navigation(["seiten/stg.py", "seiten/settings.py", "seiten/photo.py"], expanded=False)
pg.run()


st.title("STG")


st.selectbox("Sprache",("Deutsch", "Englisch", "Französisch"), key="sprache", index=None, on_change=lang_switch, placeholder="Default: Automatic")


if st.toggle("STT?"):
    lang_switch()
    value = deepgramcomp(language=st.session_state.language_code)
    st.write("Received", value)
    
    st.text_area(f"Antwort  auf speech:", gemini_request(value), height=100)

chat_box = st.container(height=300)
with chat_box:
    for message in st.session_state.context:
        st.chat_message("user").write(message["user"])
        st.chat_message("assistant").write(message["assistant"])
if prompt := st.chat_input("Say something", accept_file=True, file_type=["jpg", "jpeg", "png", "pdf"],):
    user_text = prompt.text
    uploaded_files_list = prompt.files
    with chat_box:
        user_message_display = user_text

        if uploaded_files_list:
            file_names = ", ".join([f.name for f in uploaded_files_list])
            user_message_display += f" (Dateien: {file_names})"
        st.chat_message("user").write(user_message_display)

        response_text = ""
        if uploaded_files_list: 
            for uploaded_file in uploaded_files_list:
                 if uploaded_file.type.startswith("image/"):
                     st.image(uploaded_file)
                 # Hier könntest du auch andere Dateitypen anzeigen (z.B. PDF-Vorschau, etc.)
            response_text = gemini_request(user_text, "file", uploaded_files_list)

        elif user_text: 
            response_text = gemini_request(user_text, "custom")
        else: 
             response_text = "Bitte gib Text ein oder lade eine Datei hoch."

        if response_text: 
             st.chat_message("assistant").write(response_text)

        # st.chat_message("user").write(prompt.text)
        # if not prompt["files"]:
        #     st.chat_message("assistant").write(gemini_request(prompt.text, "custom"))
        # if prompt["files"]:
        #     st.chat_message("assistant").write(gemini_request(prompt.text, "file", prompt["files"]))
        #     st.image(prompt["files"])



if st.button("Clear Session State"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.checkbox("Google-Suche aktivieren", key="search")

if st.button("Zufällige Frage testen"):
    test_prompts = ["Apfel", "Was ist die Hauptstadt von Berlin?", "Kirsche", "Hallo", "Wie hoch ist der Eiffelturm"]
    value = random.choice(test_prompts)
    st.write("Received", value)
    st.text_area(f"Antwort  auf random:", gemini_request(value), height=100)


st.link_button("Close", "https://login.schulportal.hessen.de/?url=aHR0cHM6Ly9jb25uZWN0LnNjaHVscG9ydGFsLmhlc3Nlbi5kZS8=&skin=sp&i=5120")

if st.checkbox("Verlauf anzeigen"):
    st.text_area("Konversationsverlauf:", value=str(st.session_state.context), height=200)

#if st.button("Session State"):
st.write(st.session_state)

