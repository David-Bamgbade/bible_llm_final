# import streamlit as st
# import requests
#
#
# # Streamlit UI
# st.title("📖 Ask the Bible AI")
# st.write("Ask a question, and the AI will answer based on the Bible.")
#
#
# # User input
# question = st.text_input("Enter your question:")
#
# if st.button("Ask"):
#     if question:
#         with st.spinner("Thinking..."):
#             response = requests.post("http://127.0.0.1:5000/ask", json={"question": question})
#
#             if response.status_code == 200:
#                 answer = response.json().get("answer", "No answer found.")
#                 st.success(f"Answer: {answer}")
#             else:
#                 st.error("Failed to get a response. Check if Flask is running.")
#     else:
#         st.warning("Please enter a question before clicking Ask.")

import streamlit as st
import requests

# Streamlit UI
st.title("📖 Ask the Bible AI")
st.write("Ask a question, and the AI will answer based on the Bible.")

# Let the user choose between text and voice response.
response_type = st.radio("Select response type:", ("Text", "Voice"), index=0)

# User input for the question.
question = st.text_input("Enter your question:")

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            # Build the payload with question and response type.
            payload = {
                "question": question,
                "response_type": response_type.lower()  # "text" or "voice"
            }
            response = requests.post("http://127.0.0.1:5000/ask", json=payload)

            if response.status_code == 200:
                if response_type.lower() == "voice":
                    # For voice responses, Flask returns an audio file.
                    # Play the audio using st.audio (assumes mp3 format).
                    st.audio(response.content, format="audio/mp3")
                else:
                    # For text responses, extract and display the answer.
                    answer = response.json().get("answer", "No answer found.")
                    st.success(f"Answer: {answer}")
            else:
                st.error("Failed to get a response. Check if Flask is running.")
    else:
        st.warning("Please enter a question before clicking Ask.")
