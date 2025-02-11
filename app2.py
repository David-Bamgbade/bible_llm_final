from flask import Flask, request, jsonify, send_file
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from io import BytesIO
from gtts import gTTS

app = Flask(__name__)

# Optional: Use the T5 model if you wish to further generate a response.
pre_trained_model = pipeline("text2text-generation", model="google-t5/t5-small")

# Path to your JSON dataset
filePath = "genesis.json"

# Initialize your SentenceTransformer model.
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def load_bible_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


# Load the Bible data
bible_data = load_bible_data(filePath)

# Create embeddings for each record's "text"
texts = [record["text"] for record in bible_data]
embeddings = embedder.encode(texts, convert_to_numpy=True)

# Create a FAISS index for fast similarity search.
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)


def retrieve_bible_verse(question):
    """
    Given a question, encode it and search for the most similar Bible verse in the dataset.
    Returns the matching record (a dict with keys "book", "chapter", "verse", "text")
    or None if no match is found.
    """
    query_embedding = np.array(embedder.encode([question], convert_to_numpy=True))
    _, indices = index.search(query_embedding, 1)  # retrieve the single closest record
    if indices is not None and len(indices[0]) > 0 and indices[0][0] != -1:
        return bible_data[indices[0][0]]
    else:
        return None


def answer_question(question):
    """
    Retrieves the Bible verse record that best matches the query and formats the reply.
    You can also incorporate the generation pipeline here if you wish to expand on the answer.
    """
    record = retrieve_bible_verse(question)
    if record:
        # Format the reply with citation details.
        reply = f"{record['book']} {record['chapter']}:{record['verse']} - {record['text']}"

        return reply
    else:
        return "No relevant verse found."


@app.route('/ask', methods=['POST'])
def query():
    data = request.json
    question = data.get("question")
    response_type = data.get("response_type", "text")
    if not question:
        return jsonify({"error": "Question is required"}), 400
    response = answer_question(question)

    if response_type == "voice":
        # Convert the answer text to speech using gTTS
        tts = gTTS(response, lang="en")
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        # Return the audio file with the appropriate MIME type.
        return send_file(audio_file, mimetype="audio/mpeg", as_attachment=False, download_name="answer.mp3")
    else:
        return jsonify({"answer": response})
    # return jsonify({"answer": response})


if __name__ == '__main__':
    app.run(debug=True)
