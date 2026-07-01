import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, classification_report

# ----------------------------
# Load cleaned dataset
# ----------------------------

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "dataset", "cleaned_spam.csv")

df = pd.read_csv(csv_path)

df["message"] = df["message"].fillna("")
df = df[df["message"].str.strip() != ""]

# ----------------------------
# Input and Output
# ----------------------------

X = df["message"]
y = df["label"]

# ----------------------------
# Convert text into numbers
# ----------------------------

vectorizer = TfidfVectorizer(max_features=5000)

X = vectorizer.fit_transform(X)

# ----------------------------
# Split dataset
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ----------------------------
# Models
# ----------------------------

models = {

    "Naive Bayes": MultinomialNB(),

    "SVM": CalibratedClassifierCV(
    LinearSVC(),
    cv=5
),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

}

best_accuracy = 0
best_model = None
best_name = ""

print("\n==============================")

for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)

    prediction = model.predict(X_test)

    accuracy = accuracy_score(y_test, prediction)

    print(f"Accuracy : {accuracy:.4f}")

    print(classification_report(y_test, prediction))

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model
        best_name = name

print("\n==============================")

print(f"\nBest Model : {best_name}")

print(f"Accuracy : {best_accuracy:.4f}")

# ----------------------------
# Save Model
# ----------------------------

joblib.dump(best_model, "best_model.pkl")

joblib.dump(vectorizer, "vectorizer.pkl")

print("\nModel Saved Successfully.")
print("Vectorizer Saved Successfully.")