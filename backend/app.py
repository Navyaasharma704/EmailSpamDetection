from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os


# -----------------------------
# Create Flask App
# -----------------------------
app = Flask(__name__)
CORS(app)


# -----------------------------
# Load Saved Model & Vectorizer
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(
    os.path.join(BASE_DIR, "best_model.pkl")
)

vectorizer = joblib.load(
    os.path.join(BASE_DIR, "vectorizer.pkl")
)


# -----------------------------
# Home Route
# -----------------------------
@app.route("/")
def home():

    return jsonify({
        "message": "Email Spam Detection API is Running Successfully 🚀"
    })


# -----------------------------
# Prediction Route
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()


        if not data or "email" not in data:

            return jsonify({
                "error": "Please provide email text."
            }), 400


        email = data["email"]


        # Convert email text into numbers using TF-IDF
        email_vector = vectorizer.transform([email])


        # Predict using ML model
        prediction = model.predict(email_vector)


        # Convert prediction into label
        if prediction[0] == 1:
            result = "Spam"
        else:
            result = "Not Spam"


        return jsonify({
            "result": result
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500



# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":

    app.run(debug=True)