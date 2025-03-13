import streamlit as st
from mytestcomponent import mytestcomponent
value = mytestcomponent(my_input_value="hello there")
st.write("Received", value)