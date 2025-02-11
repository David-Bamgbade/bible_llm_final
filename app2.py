from flask import Flask, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

app = Flask(__name__)

# Optional: Use the T5 model if you wish to further generate a response.
pre_trained_model = pipeline("text2text-generation", model="google-t5/t5-small")

# Path to your JSON dataset
filePath = "genesis.json"

# Initialize your SentenceTransformer model.
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# Function to load Bible data from a JSON file.
# The JSON file should contain a list of records, for example:
# [
#   {
#     "book": "Genesis",
#     "chapter": 1,
#     "verse": 6,
#     "text": "And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters."
#   },
#   ...
# ]
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

        # --- OPTIONAL: Further refine the answer using the generation pipeline ---
        # If you want to provide a more expansive response, you might do something like:
        #
        # prompt = (
        #     f"You are a pastor. Based on the Bible verse:\n"
        #     f"{reply}\n\n"
        #     f"Answer the following question:\n{question}\n"
        #     f"Provide context and explanation in your response."
        # )
        # result = pre_trained_model(prompt, max_length=4000)
        # generated_answer = result[0].get('generated_text', reply)
        # return generated_answer
        #
        # Otherwise, simply return the formatted verse:
        return reply
    else:
        return "No relevant verse found."


@app.route('/ask', methods=['POST'])
def query():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required"}), 400
    response = answer_question(question)
    return jsonify({"answer": response})


if __name__ == '__main__':
    app.run(debug=True)
