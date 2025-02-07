from flask import Flask, request, jsonify
from transformers import pipeline
# import torch
#
# torch.set_num_threads(1)  # Reduce CPU threading to avoid overload
# torch.device("cpu")  # Ensure CPU-only execution


app = Flask(__name__)

pre_trained_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

filePath = "genesis.txt"


# Function to load Bible data and split into chunks
def load_bible_in_chunks(file_path, chunk_size=1000):
    bible_data = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(0, len(lines), chunk_size):
            bible_data.append("".join(lines[i:i + chunk_size]))  # Create chunks
    return bible_data


bible_context = load_bible_in_chunks(filePath)


# Load the Bible in chunks


# Function to answer the question based on context (Bible chunks)
def answer_question(question):
    # Here we select the chunk closest to the question's context (for simplicity, first chunk)
    context = bible_context[0]  # Modify logic to select context dynamically
    result = pre_trained_model(question=question, context=context)
    return result['answer']


@app.route('/ask', methods=['POST'])
def query():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"Error": "Question Is Required"}), 400
    response = answer_question(question)
    return jsonify({"answer": response})


if __name__ == '__main__':
    app.run(debug=True)