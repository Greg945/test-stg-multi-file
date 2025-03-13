import streamlit as st
from mycomponent import mycomponent
import streamlit.components.v1 as components
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import random
import json
import os
import time
from threading import Timer



client = genai.Client(api_key="AIzaSyA3iQXk6-M5XQhzLIMO3SfEAKDPRunTHP8")

google_search_tool = Tool(google_search=GoogleSearch())

lever_mycomp = 0
if 'search' not in st.session_state:
    st.session_state['search'] = False

if 'response' not in st.session_state:
    st.session_state['response'] = ''


if 'sprache' not in st.session_state:
    st.session_state['sprache'] = 'Deutsch'

if 'language_code' not in st.session_state:
    st.session_state['language_code'] = 'de-DE'

if "context" not in st.session_state:
    st.session_state.context = [{"role": "user", "content": "hallo"}]  #load_chat_history()


CHAT_FILE = "chat_history.json"

DEFAULT_LANGUAGE = "de-DE"
API_DELAY = 5  # Sekunden

# Systemanweisung für Gemini
SYS_INSTRUCT = ('Du bist ein mithörender Assistent in einem Klassenzimmer. Wenn du eine Frage hörst, beantworte sie bitte normal. '
                'Wenn es keine Frage ist, antworte nur mit "Ignoriert". Außerdem bekommst du immer den Konversationsverlauf, '
                'den du nur benutzt, falls du Informationen daraus zur Beantwortung der Frage brauchst.')



def load_chat_history():
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history(chat_history):
    with open(CHAT_FILE, "w") as f:
        json.dump(chat_history, f)


def gemini_request(text):
    context = st.session_state.context
    search_enabled=st.session_state.get("search", False)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=SYS_INSTRUCT,
                tools=[google_search_tool] if search_enabled else [],
                response_modalities=["TEXT"]
            ),
            contents=f'Konversations Verlauf:"{context}" Das hier ist das gehörte im Klassenraum: {text}'
        )
        response_text = response.text.strip()
    except Exception as e:
        response_text = f"Fehler bei der API-Anfrage: {e}"
        st.error(response_text)

    st.session_state.context.append({"role": "user", "content": text})
    st.session_state.context.append({"role": "assistant", "content": response_text})

    # save_chat_history(st.session_state.context)
    st.session_state.response = response_text
    st.text_area("Antwort:", st.session_state.response, height=100)
    print('Apicall for:', text)
    print(response_text)



def reset_flag():
    global is_waiting
    print("Waiting befor reset: ", is_waiting)
    is_waiting = False #geht bviellcit irgendwie nicht?
    print("reset after: ", is_waiting)
    mycomponent(my_input_value="change")
    event_daten = {"message": "Hallo von Streamlit!"}
    components.html(f"""
        <script>
            window.dispatchEvent(new CustomEvent('streamlit:customEvent', {{detail: {event_daten}}}));
        </script>
    """)
    print("Ereignis ausgelöst!")
    #if st.session_state.queue != []:
    #    delayed_api_call()


def lang_switch():
    language_codes = {"Deutsch": "de-DE", "Englisch": "en-GB", "Französisch": "fr-FR"}
    st.session_state.language_code = language_codes.get(st.session_state.sprache, DEFAULT_LANGUAGE)


##################################  UI  #########################################

st.title("STG")


st.selectbox("Sprache",("Deutsch", "Englisch", "Französisch"), key="sprache", on_change=lang_switch)


if st.toggle("STT?"):
    value = mycomponent(language=st.session_state.language_code)
    st.write("Received", value)
    gemini_request(value)



text_input = st.text_input("Oder Eingabe per Tastatur", key="text_input")

if st.button("Senden"):
    if text_input:
        gemini_request(text_input)


if st.button("Clear Session State"):
    for key in st.session_state.keys():
        del st.session_state[key]

st.checkbox("Google-Suche aktivieren", key="search")

if st.button("Zufällige Frage testen"):
    test_prompts = ["Apfel", "Was ist die Hauptstadt von Berlin?", "Kirsche", "Hallo", "Wie hoch ist der Eiffelturm"]
    value = random.choice(test_prompts)
    st.write("Received", value)
    gemini_request(value)


st.link_button("Close", "https://login.schulportal.hessen.de/?url=aHR0cHM6Ly9jb25uZWN0LnNjaHVscG9ydGFsLmhlc3Nlbi5kZS8=&skin=sp&i=5120")

if st.checkbox("Verlauf anzeigen"):
    st.text_area("Konversationsverlauf:", value=str(st.session_state.context), height=200)

#if st.button("Session State"):
st.write(st.session_state)