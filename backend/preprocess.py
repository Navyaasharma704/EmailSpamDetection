import pandas as pd
import os
import string
import nltk

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data (only first time)
nltk.download("stopwords")

# Load dataset
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "dataset", "spam.csv")

df = pd.read_csv(csv_path, encoding="latin-1")

# Keep only useful columns
df = df[["v1", "v2"]]

# Rename columns
df.columns = ["label", "message"]

# Convert labels to numbers
df["label"] = df["label"].map({"ham": 0, "spam": 1})

# Create stemmer
stemmer = PorterStemmer()

def clean_text(text):
    text = text.lower()

    # Remove punctuation
    text = "".join(char for char in text if char not in string.punctuation)

    words = text.split()

    # Remove stopwords and stem words
    words = [
        stemmer.stem(word)
        for word in words
        if word not in stopwords.words("english")
    ]

    return " ".join(words)

# Clean all messages
df["message"] = df["message"].apply(clean_text)

# Remove empty or null messages
df["message"] = df["message"].fillna("")
df = df[df["message"].str.strip() != ""]

print(df.head())

# Save cleaned dataset
output_path = os.path.join(base_dir, "dataset", "cleaned_spam.csv")
df.to_csv(output_path, index=False)

print("\n✅ Cleaned dataset saved successfully!")