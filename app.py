import streamlit as st

st.set_page_config(page_title="BioMatrix", layout="centered")

st.title("Welcome to BioMatrix v2.0")
st.write("This is a test deployment of the Streamlit app using Render.")

if st.button("Click me"):
    st.success("App is working!")
