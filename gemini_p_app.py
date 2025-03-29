import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import numpy as np
import queue
import threading
import os
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)

# Deepgram API-Schlüssel aus Streamlit Secrets laden
DEEPGRAM_API_KEY = st.secrets.get("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    st.error("Deepgram API-Schlüssel nicht gefunden. Bitte in Streamlit Secrets hinterlegen.")
    st.stop()

# Thread-sichere Queue für Transkriptionsergebnisse
transcript_queue = queue.Queue()

# Deepgram WebSocket-Verbindung
dg_connection = None

def audio_frame_callback(frame: av.AudioFrame):
    global dg_connection
    if dg_connection and dg_connection.connected:
        try:
            # Audio-Frame in das von Deepgram erwartete Format konvertieren (Linear PCM)
            frame.pts = None  # Zurücksetzen der Presentation Timestamp
            for packet in frame.to_bytes():
                dg_connection.send(packet)
        except Exception as e:
            print(f"Fehler beim Senden des Audio-Frames an Deepgram: {e}")
    print(frame)
    return frame

def on_open(open_response, *args, **kwargs):
    print(f"Deepgram WebSocket geöffnet: {open_response}")

def on_message(result, **kwargs):
    print("message")
    if 'channel' in result and 'alternatives' in result['channel'] and result['channel']['alternatives']:
        transcript = result['channel']['alternatives']['transcript']
        if transcript:
            transcript_queue.put(transcript)

def on_error(error, **kwargs):
    print(f"Deepgram WebSocket-Fehler: {error}")

def on_close(close_response, **kwargs):
    print(f"Deepgram WebSocket geschlossen: {close_response}")

def main():
    st.title("Live-Audio-Transkription mit Streamlit und Deepgram")

    global dg_connection

    if "transcription" not in st.session_state:
        st.session_state["transcription"] = ""

    webrtc_ctx = webrtc_streamer(
        key="live-transcription",
        #audio_config=True,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.state.playing:
        if dg_connection is None or not dg_connection.connected:
            try:
                config = DeepgramClientOptions(
                    options={"keepalive": "true"}
                )
                print(DEEPGRAM_API_KEY)
                client = DeepgramClient(DEEPGRAM_API_KEY, config)
                options = LiveOptions(
                    model="nova-2",  # Oder ein anderes gewünschtes Modell
                    punctuate=True,
                    language="de-DE",
                    interim_results=True,
                    encoding="linear16",
                    channels=1,
                    sample_rate= 48000, # Abtastrate vom Stream übernehmen oder Standardwert verwenden 
                    #webrtc_ctx.audio_config.sample_rate if webrtc_ctx.audio_config else
                )
                dg_connection = client.listen.websocket.v("1")
                dg_connection.on(LiveTranscriptionEvents.Open, on_open)
                dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
                dg_connection.on(LiveTranscriptionEvents.Error, on_error)
                dg_connection.on(LiveTranscriptionEvents.Close, on_close)
                dg_connection.start(options)
                st.info("Deepgram WebSocket verbunden.")
            except Exception as e:
                st.error(f"Fehler beim Verbinden mit Deepgram: {e}")
                dg_connection = None

        while not transcript_queue.empty():
            transcript = transcript_queue.get_nowait()
            st.session_state["transcription"] += transcript + " "
            st.experimental_rerun()

    else:
        if dg_connection and dg_connection.connected:
            dg_connection.finish()
            dg_connection = None
            st.info("Deepgram WebSocket geschlossen.")
        st.session_state["transcription"] = ""

    st.subheader("Live-Transkription:")
    st.text_area("", st.session_state["transcription"], height=300)

if __name__ == "__main__":
    main()