import streamlit as st
from gtts import gTTS
import os
import pygame
from transformers import pipeline
import io

# Load the Question Answering Model
pre_trained_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Load the Bible text
filePath = "bible.txt"


def load_bible_in_chunks(file_path, chunk_size=1000):
    bible_data = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(0, len(lines), chunk_size):
            bible_data.append("".join(lines[i:i + chunk_size]))  # Create chunks
    return bible_data


bible_context = load_bible_in_chunks(filePath)


# Function to answer the question
def answer_question(question):
    context = bible_context[0]  # Modify to select relevant context dynamically
    result = pre_trained_model(question=question, context=context)
    return result['answer']


# Function to convert text to speech
def text_to_speech(text):
    # tts = gTTS(text=text, lang='en')

    tts = gTTS(text=text, lang='en', slow=False)

    # Create an in-memory buffer to store the audio
    audio_stream = io.BytesIO()

    # Save the audio to the in-memory buffer instead of a file
    tts.save(audio_stream)

    # Rewind the buffer to the beginning
    audio_stream.seek(0)

    # Initialize pygame mixer for audio playback
    pygame.mixer.init()

    # Load the audio from the in-memory buffer
    pygame.mixer.music.load(audio_stream, "mp3")

    # Play the audio
    pygame.mixer.music.play()

    # Wait until the audio is finished
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # tts.save("output.mp3")
    # Save audio to a byte stream
    # fp = io.BytesIO()
    # tts.save(fp)
    # fp.seek(0)

    # Play audio directly from the byte stream
    # pygame.mixer.music.load(fp)
    # pygame.mixer.music.play()
    # output_file = os.path.join(os.getcwd(), "output.mp3")
    #
    # # Play the audio
    # pygame.mixer.init()
    # pygame.mixer.music.load("output.mp3")
    # pygame.mixer.music.play()
    #
    # # Wait for audio to finish
    # while pygame.mixer.music.get_busy():
    #     continue


# Streamlit UI
st.title("📖 Ask the Bible AI")

question = st.text_input("Enter your question:")

# Checkbox for audio option
play_audio = st.checkbox("Read answer aloud")

if st.button("Get Answer"):
    if question:
        answer = answer_question(question)
        st.write("**Answer:**", answer)

        # If user wants audio, play it
        if play_audio:
            text_to_speech(answer)
            st.success("🔊 Answer is being read aloud!")
    else:
        st.error("⚠️ Please enter a question.")
