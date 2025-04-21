import streamlit as st

st.session_state.test_selector = "Home phone"


option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
    index=None,
    key="test_selector"
)

st.write("You selected:", option)

st.write(st.session_state)