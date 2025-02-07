import streamlit as st
import requests
import pygame

# Streamlit UI
st.title("📖 Ask the Bible AI")
st.write("Ask a question, and the AI will answer based on the Bible.")




# User input
question = st.text_input("Enter your question:")

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post("http://127.0.0.1:5000/ask", json={"question": question})

            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.success(f"Answer: {answer}")
            else:
                st.error("Failed to get a response. Check if Flask is running.")
    else:
        st.warning("Please enter a question before clicking Ask.")
