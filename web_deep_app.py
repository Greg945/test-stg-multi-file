import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from deepgram import Microphone
import pydub

def audio_frame_callback(frame):
    sound = pydub.AudioSegment(
                    data=frame.to_ndarray().tobytes(),
                    sample_width=frame.format.bytes,
                    frame_rate=frame.sample_rate,
                    channels=len(frame.layout.channels),
                )
    print(sound)

webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        #mode=WebRtcMode.SENDONLY,
        #audio_receiver_size=1024,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"video": False, "audio": True},
    )

#if st.button("print"):

# Open a microphone stream on the default input device
#microphone = Microphone(print)

        # start microphone
#microphone.start()