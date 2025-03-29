import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, RTCConfiguration, WebRtcMode
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
import threading

DEEPGRAM_API_KEY = "861ef76d80da6f7535d9f3361dd139e2dd26a24d" # Replace with your actual key

client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class DeepgramTranscriptionProcessor(AudioProcessorBase):
    def __init__(self):
        config = DeepgramClientOptions(
            options={"keepalive": "true"}
            mode=WebRtcMode.SENDONLY,
        )
        self.deepgram_client = DeepgramClient(DEEPGRAM_API_KEY, config)
        self.dg_connection = None
        self.is_finals = []
        self.output_area = None

    def on_open(self, *args, **kwargs):
        print("Deepgram WebSocket connection opened")
        self.is_finals = []

    def on_message(self, result, **kwargs):
        print("message: " + result)
        if isinstance(result, dict) and 'channel' in result and 'alternatives' in result['channel'] and len(result['channel']['alternatives']) > 0:
            transcript = result['channel']['alternatives'].get('transcript', '')
            if transcript:
                if result.get('is_final'):
                    self.is_finals.append(transcript)
                    if result.get('speech_final'):
                        utterance = " ".join(self.is_finals)
                        print(f"Speech Final: {utterance}")
                        if self.output_area:
                            self.output_area.text_area("Live Transcribed Text", utterance, height=100)
                            st.session_state.live_transcript = utterance # Store for Gemini request
                        self.is_finals = []

    def on_close(self, *args, **kwargs):
        print("Deepgram WebSocket connection closed")

    def recv(self, frame):
        if self.dg_connection and self.dg_connection.is_connected:
            self.dg_connection.send(frame.to_ndarray().tobytes())
        return frame

    def start_deepgram(self):
        options: LiveOptions = LiveOptions(
            model="nova-2",
            language="de-DE",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=300,
        )
        self.dg_connection = self.deepgram_client.listen.websocket.v("1")
        self.dg_connection.on(LiveTranscriptionEvents.Open, self.on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Close, self.on_close)

        try:
            self.dg_connection.start(options)
        except Exception as e:
            print(f"Could not connect to Deepgram WebSocket: {e}")

def stt_browser():
    if "live_transcript" not in st.session_state:
        st.session_state.live_transcript = ""
    ctx = webrtc_streamer(
        key="deepgram-stt",
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=DeepgramTranscriptionProcessor,
    )
    if ctx and ctx.audio_processor:
        ctx.audio_processor.output_area = st.empty()
        if not ctx.audio_processor.dg_connection or not ctx.audio_processor.dg_connection.is_connected:
            threading.Thread(target=ctx.audio_processor.start_deepgram).start()

# Replace the original stt() function call with stt_browser()
settings = st.Page("seiten/settings.py", title="Settings", icon=":material/settings:")
photo = st.Page("seiten/settings.py", title="Photo", icon=":material/camera:")
stg = st.Page("seiten/stg.py", title="STG", icon=":material/camera:")

st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

pg = st.navigation(["seiten/stg.py", "seiten/settings.py", "seiten/photo.py"])
pg.run()


st.title("STG")


# st.selectbox("Sprache",("Deutsch", "Englisch", "Französisch"), key="sprache", index=None, on_change=lang_switch, placeholder="Default: Automatic")


#if st.button("STT Start"):
    #lang_switch()
stt_browser()

# st.text_area(f"Antwort  auf text input:{st.session_state.output}", height=100, value=st.session_state.output)

# if "live_transcript" in st.session_state and st.session_state.live_transcript:
#     if st.button("Senden transkribierten Text"):
#         st.text_area(f"Antwort auf Live-Transkription:{gemini_request(st.session_state.live_transcript)}", height=100)


text_input = st.text_input("Oder Eingabe per Tastatur", key="text_input")

# if st.button("Senden"):
#     if text_input:
#         st.text_area(f"Antwort  auf text input:{gemini_request(text_input)}", height=100)


if st.button("Clear Session State"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.checkbox("Google-Suche aktivieren", key="search")

# if st.button("Zufällige Frage testen"):
#     test_prompts =
#     value = random.choice(test_prompts)
#     st.write("Received", value)
#     st.text_area(f"Antwort  auf text input:{gemini_request(value)}", height=100)


st.link_button("Close", "https://login.schulportal.hessen.de/?url=aHR0cHM6Ly9jb25uZWN0LnNjaHVscG9ydGFsLmhlc3Nlbi5kZS8=&skin=sp&i=5120")

if st.checkbox("Verlauf anzeigen"):
    st.text_area("Konversationsverlauf:", value=str(st.session_state.context), height=200)

if st.button("Session State"):
    st.write(st.session_state)