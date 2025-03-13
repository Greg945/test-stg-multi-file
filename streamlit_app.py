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
search = "false"

if 'response' not in st.session_state:
    st.session_state['response'] = ''


if 'sprache' not in st.session_state:
    st.session_state['sprache'] = 'Deutsch'

if 'queue' not in st.session_state:
    st.session_state.queue = []

if 'is_waiting' not in st.session_state:
      st.session_state.is_waiting = False

if 'is_waiting' in globals():
    st.session_state.is_waiting = is_waiting
    print("change zu: ", is_waiting)

if 'is_waiting' not in globals():
        is_waiting = None



#if st.session_state.is_waiting_def == False:
#is_waiting = ""
#    st.session_state.is_waiting_def = True

#if 'is_waiting' not in globals():
#    print("rewrite")
#    is_waiting = False

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


def gemini_request(text, search_enabled=False):
    context = st.session_state.context
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

def delayed_api_call():
    final_text = " ".join(st.session_state.queue)
    st.session_state.queue = []
    gemini_request(final_text, search_enabled=st.session_state.get("search", False))


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


def value_processing(value):
    event_daten = {"message": "Hallo von Streamlit!"}
    components.html(f"""
        <script>
            window.dispatchEvent(new CustomEvent('streamlit:customEvent', {{detail: {event_daten}}}));
        </script>
    """)
    global is_waiting
    print("Received", value)
    print("Waiting: ", st.session_state.is_waiting)
    print("Waiting2: ", is_waiting)
    print('halllllllllllllooooooooooo')
    if value:
        print("Value da")
        st.session_state.queue.append(value)
        if st.session_state.is_waiting == False or is_waiting == False:
            st.session_state.is_waiting = True
            is_waiting = True
            print("          waiting jetzt True")
            delayed_api_call()
            thread = Timer(5.0, reset_flag)
            thread.start()
        else:
            print("blocked!!!!!!!!!!!!")

##################################  UI  #########################################

st.title("STG")


st.selectbox("Sprache",("Deutsch", "Englisch", "Französisch"), key="sprache", on_change=lang_switch)


if st.toggle("STT?"):
    value = mycomponent(my_input_value="hello there")
    st.write("Received", value)
    value_processing(value)







text_input = st.text_input("Oder Eingabe per Tastatur", key="text_input")

if st.button("Senden"):
    if text_input:
        gemini_request(text_input, search_enabled=st.session_state.get("search", False))


if st.button("Clear Session State"):
    for key in st.session_state.keys():
        del st.session_state[key]

st.session_state.search = st.checkbox("Google-Suche aktivieren", value=st.session_state.get("search", False))

if st.button("Zufällige Frage testen"):
    test_prompts = ["Apfel", "Was ist die Hauptstadt von Berlin?", "Kirsche", "Hallo", "Wie hoch ist der Eiffelturm"]
    value = random.choice(test_prompts)
    st.write("Received", value)
    value_processing(value)


st.link_button("Close", "https://login.schulportal.hessen.de/?url=aHR0cHM6Ly9jb25uZWN0LnNjaHVscG9ydGFsLmhlc3Nlbi5kZS8=&skin=sp&i=5120")

if st.checkbox("Verlauf anzeigen"):
    st.text_area("Konversationsverlauf:", value=str(st.session_state.context), height=200)

#if st.button("Session State"):
st.write(st.session_state)