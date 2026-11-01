
import os
import re
import io
import base64
import secrets
import sqlite3

import joblib
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from database import create_database, get_connection


# --------------------------------------------------
# 1. FLASK CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")
VECTOR_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
COMPARISON_PATH = os.path.join(BASE_DIR, "model_comparison.csv")
CONFUSION_PATH = os.path.join(BASE_DIR, "confusion_matrix.png")

PORT = int(os.environ.get("PORT", 5000))


# --------------------------------------------------
# 2. LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("best_model.pkl not found!")

model = joblib.load(MODEL_PATH)

if not os.path.exists(VECTOR_PATH):
    raise FileNotFoundError("vectorizer.pkl not found!")

vectorizer = joblib.load(VECTOR_PATH)

print("Machine Learning model loaded successfully!")
print("TF-IDF Vectorizer loaded successfully!")


# --------------------------------------------------
# 3. DATABASE INITIALIZATION
# --------------------------------------------------

create_database()


# --------------------------------------------------
# 4. AUTHENTICATION
# --------------------------------------------------

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Login required"}), 401

        token = auth_header.split(" ", 1)[1]

        connection = get_connection()

        try:
            user = connection.execute(
                """
                SELECT user_id
                FROM user_sessions
                WHERE token = ?
                """,
                (token,)
            ).fetchone()

        finally:
            connection.close()

        if not user:
            return jsonify({"error": "Invalid or expired session"}), 401

        request.user_id = user["user_id"]

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# 5. REGISTER
# --------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must contain at least 6 characters"
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        connection.commit()

        return jsonify({
            "message": "Registration successful"
        }), 201

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Username already exists"
        }), 409

    finally:
        connection.close()


# --------------------------------------------------
# 6. LOGIN
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if not user or not check_password_hash(
            user["password_hash"], password
        ):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        token = secrets.token_urlsafe(32)

        connection.execute(
            """
            INSERT INTO user_sessions (token, user_id)
            VALUES (?, ?)
            """,
            (token, user["id"])
        )

        connection.commit()

        return jsonify({
            "message": "Login successful",
            "token": token,
            "username": user["username"]
        }), 200

    finally:
        connection.close()


# --------------------------------------------------
# 7. LOGOUT
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    token = request.headers.get("Authorization", "").split(" ", 1)[1]

    connection = get_connection()

    try:

        connection.execute(
            "DELETE FROM user_sessions WHERE token = ?",
            (token,)
        )

        connection.commit()

        return jsonify({
            "message": "Logout successful"
        }), 200

    finally:
        connection.close()


# --------------------------------------------------
# 8. SPAM INDICATORS
# --------------------------------------------------

def find_indicators(email):

    text = email.lower()

    indicators = []

    patterns = {
        "Money or prize": [
            "winner", "won", "cash prize", "money",
            "lottery", "reward", "free cash", "jackpot",
            "500000", "million"
        ],

        "Promotional language": [
            "congratulations", "claim now", "limited offer",
            "free gift", "click here", "act now",
            "exclusive offer"
        ],

        "Urgent or suspicious language": [
            "urgent", "immediately", "account suspended",
            "verify now", "act immediately"
        ],

        "Suspicious account requests": [
            "share your otp", "send your otp",
            "password required", "bank details"
        ]
    }

    for category, words in patterns.items():

        matched = [
            word for word in words if word in text
        ]

        if matched:
            indicators.append({
                "category": category,
                "examples": matched
            })

    return indicators


# --------------------------------------------------
# 9. HYBRID SPAM DETECTION
# --------------------------------------------------

def is_strong_spam(email):

    text = email.lower()

    has_prize = bool(re.search(
        r"\b(congratulations|congrats|winner|won|lottery|jackpot|prize|reward)\b",
        text
    ))

    has_money = bool(re.search(
        r"(?:rs\.?|inr|rupees?)\s*[\d,]+|[\d,]+\s*(?:rs\.?|inr|rupees?)|₹\s*[\d,]+",
        text
    ))

    has_action = bool(re.search(
        r"\b(click here|claim now|claim your|claim it|tap here|verify now)\b",
        text
    ))

    has_otp_risk = bool(re.search(
        r"\b(share your otp|send your otp|enter your otp)\b",
        text
    ))

    has_lottery_action = (
        "lottery" in text and has_action
    )

    return (
        (has_prize and has_money and has_action)
        or has_lottery_action
        or has_otp_risk
    )


# --------------------------------------------------
# 10. HOME ROUTE
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Email Spam Detection API is running",
        "status": "healthy",
        "version": "3.1"
    })


# --------------------------------------------------
# 11. HEALTH CHECK
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "model": "Random Forest",
        "hybrid_detection": True
    })


# --------------------------------------------------
# 12. EMAIL PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
@login_required
def predict():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip()

    if not email:
        return jsonify({
            "error": "Please enter an email message"
        }), 400

    if len(email) > 20000:
        return jsonify({
            "error": "Email is too long"
        }), 400

    try:

        # Convert email text into TF-IDF numerical features
        email_vector = vectorizer.transform([email])

        # Machine Learning prediction
        prediction = model.predict(email_vector)[0]

        probabilities = model.predict_proba(email_vector)[0]

        classes = list(model.classes_)

        spam_index = classes.index(1)
        not_spam_index = classes.index(0)

        spam_probability = float(probabilities[spam_index])
        not_spam_probability = float(probabilities[not_spam_index])

        ml_result = "Spam" if int(prediction) == 1 else "Not Spam"

        ml_confidence = (
            spam_probability
            if ml_result == "Spam"
            else not_spam_probability
        )

        # Hybrid safety check
        rule_triggered = is_strong_spam(email)

        if rule_triggered:
            result = "Spam"
            explanation = (
                "The email contains strong suspicious patterns "
                "related to prize claims, money, suspicious actions "
                "or OTP requests. Hybrid detection classified it as spam."
            )
            detection_method = "Hybrid Detection"

        else:
            result = ml_result
            explanation = (
                "The Random Forest machine learning model classified "
                "this email as " + result + "."
            )
            detection_method = "Random Forest ML"

        confidence = round(ml_confidence * 100, 2)

        indicators = find_indicators(email)

        # Save prediction in user-specific history
        connection = get_connection()

        try:

            connection.execute(
                """
                INSERT INTO prediction_history
                (user_id, email, prediction, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (
                    request.user_id,
                    email,
                    result,
                    confidence
                )
            )

            connection.commit()

        finally:
            connection.close()

        return jsonify({

            "result": result,

            "confidence": confidence,
            "confidence_percent": confidence,

            "indicators": indicators,
            "indicator_count": len(indicators),

            "explanation": explanation,

            "detection_method": detection_method,

            "ml_prediction": ml_result,

            "spam_probability": round(spam_probability * 100, 2),

            "not_spam_probability": round(
                not_spam_probability * 100, 2
            )

        }), 200

    except Exception as error:

        app.logger.exception("Prediction error")

        return jsonify({
            "error": "Prediction failed. Please try again."
        }), 500


# --------------------------------------------------
# 13. PREDICTION HISTORY
# --------------------------------------------------

@app.route("/history", methods=["GET"])
@login_required
def history():

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT id, email, prediction, confidence, created_at
            FROM prediction_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 100
            """,
            (request.user_id,)
        ).fetchall()

        records = []

        for row in rows:

            records.append({
                "id": row["id"],
                "email": row["email"],
                "prediction": row["prediction"],
                "confidence": row["confidence"],
                "created_at": row["created_at"]
            })

        return jsonify(records), 200

    finally:
        connection.close()


# --------------------------------------------------
# 14. CHART GENERATION
# --------------------------------------------------

def chart_to_base64(figure):

    buffer = io.BytesIO()

    figure.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        dpi=120
    )

    buffer.seek(0)

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    plt.close(figure)

    return encoded


# --------------------------------------------------
# 15. PREDICTION STATISTICS AND GRAPHS
# --------------------------------------------------

@app.route("/stats", methods=["GET"])
@login_required
def stats():

    connection = get_connection()

    try:

        counts = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN prediction = 'Spam' THEN 1 ELSE 0 END) AS spam,
                SUM(CASE WHEN prediction = 'Not Spam' THEN 1 ELSE 0 END) AS not_spam
            FROM prediction_history
            WHERE user_id = ?
            """,
            (request.user_id,)
        ).fetchone()

        total = counts["total"] or 0
        spam = counts["spam"] or 0
        not_spam = counts["not_spam"] or 0

    finally:
        connection.close()

    # User prediction chart
    fig1, ax1 = plt.subplots(figsize=(7, 4))

    ax1.bar(
        ["Spam", "Not Spam"],
        [spam, not_spam]
    )

    ax1.set_title("Your Email Prediction Statistics")
    ax1.set_ylabel("Number of Emails")

    prediction_chart = chart_to_base64(fig1)

    # Model comparison chart
    model_comparison_chart = None

    if os.path.exists(COMPARISON_PATH):

        try:

            df = pd.read_csv(COMPARISON_PATH)

            model_column = next(
                (c for c in df.columns if c.lower() == "model"),
                df.columns[0]
            )

            f1_column = next(
                (c for c in df.columns if "f1" in c.lower()),
                None
            )

            if f1_column:

                fig2, ax2 = plt.subplots(figsize=(7, 4))

                ax2.bar(
                    df[model_column].astype(str),
                    pd.to_numeric(df[f1_column], errors="coerce")
                )

                ax2.set_title("Machine Learning Model Comparison")
                ax2.set_ylabel("F1 Score")
                ax2.set_ylim(0, 1)

                plt.xticks(rotation=0)

                model_comparison_chart = chart_to_base64(fig2)

        except Exception:

            app.logger.exception("Model comparison chart error")

    # Confusion matrix
    confusion_matrix = None

    if os.path.exists(CONFUSION_PATH):

        try:

            with open(CONFUSION_PATH, "rb") as image_file:

                confusion_matrix = base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

        except Exception:

            app.logger.exception("Confusion matrix loading error")

    return jsonify({

        "total": total,
        "spam": spam,
        "not_spam": not_spam,

        "total_analyzed": total,
        "spam_count": spam,
        "not_spam_count": not_spam,

        "prediction_chart": prediction_chart,

        "model_comparison_chart": model_comparison_chart,

        "confusion_matrix": confusion_matrix

    }), 200


# --------------------------------------------------
# 16. RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=PORT,
        debug=False
    )
