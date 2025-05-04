import streamlit as st

import pandas as pd
import numpy as np

st.session_state.test_selector = "Home phone"


option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
    index=None,
    key="test_selector"
)

st.write("You selected:", option)

st.write(st.session_state)

df = pd.DataFrame(
    {
        "name": ["Roadmap", "Extras", "Issues"],
        "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
        "stars": [1, 2, 3],
        "views_history": [1, 2, 3],
    }
)

print(df)

event = st.dataframe(
    df,
    #column_config=column_configuration,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)