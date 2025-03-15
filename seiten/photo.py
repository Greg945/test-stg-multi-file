import streamlit as st

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

    st.session_state.context.append({"user": text, "assistant": response_text})

    save_chat_history(st.session_state.context)
    print('Apicall for:', text)
    print(response_text)
    return response_text


st.header("photo")

st.write("phtototo")