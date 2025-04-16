import streamlit as st
import json
import pandas as pd
import datetime
import csv



st.header("Settings")

st.write("einstellungen")

model = st.text_input("Deepgram Model", key="model")

df = pd.read_csv("stundenplan2.csv")
edited_df = st.data_editor(
    df,
    column_config={},
    num_rows="dynamic"
    )

# Speichern als JSON
if st.button("Als JSON speichern"):
    # Konvertiere DataFrame zu JSON
    json_data = edited_df.to_json(orient='records', force_ascii=False)
    
    # Speichere JSON in Datei
    with open("stundenplan.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    
    print(json_data)

if st.button("print"):
    print(df)