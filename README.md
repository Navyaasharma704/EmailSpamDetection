# 📧 Email Spam Detection System

## 📖 Overview

The Email Spam Detection System is a Machine Learning web application that predicts whether an email message is **Spam** or **Not Spam**.

The user enters an email message into the application, and the trained Machine Learning model analyzes the text and displays the prediction instantly.

This project demonstrates the complete Machine Learning workflow, from data preprocessing and model training to frontend-backend integration.

---

## 🚀 Features

- Detects Spam and Not Spam emails
- User-friendly web interface
- Fast predictions using Machine Learning
- React-based frontend
- Flask-based backend
- Trained Machine Learning model
- Clean and responsive UI

---

## 🛠 Technologies Used

### Frontend
- React.js
- HTML5
- CSS3
- JavaScript
- Axios

### Backend
- Python
- Flask
- Flask-CORS

### Machine Learning
- Scikit-learn
- Pandas
- NumPy
- Pickle

---

## 📂 Project Structure

```
EmailSpamDetection/
│
├── backend/
│   ├── app.py
│   ├── train_model.py
│   ├── predict.py
│   ├── preprocess.py
│   ├── best_model.pkl
│   ├── vectorizer.pkl
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
│
├── dataset/
│   ├── spam.csv
│   ├── cleaned_spam.csv
│   └── email_spam_dataset.csv
│
└── README.md
```

---

## ⚙️ How It Works

1. User enters an email message.
2. React sends the message to the Flask backend.
3. Flask preprocesses the text.
4. The trained Machine Learning model predicts whether the email is Spam or Not Spam.
5. The prediction is displayed on the screen.

---

## 📊 Machine Learning Workflow

- Data Collection
- Data Cleaning
- Text Preprocessing
- Feature Extraction (TF-IDF Vectorization)
- Model Training
- Model Evaluation
- Model Saving
- Prediction

---

## 💻 Installation

### Clone the Repository

```bash
git clone https://github.com/Navyaasharma704/EmailSpamDetection.git
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## 📸 Screenshots

### Home Page

*(Add a screenshot here after deployment.)*

### Spam Prediction

*(Add a screenshot showing a Spam prediction.)*

### Not Spam Prediction

*(Add a screenshot showing a Not Spam prediction.)*

---

## 🎯 Future Improvements

- Gmail API integration for automatic email detection
- Mobile application
- User authentication
- Real-time email monitoring
- Multi-language spam detection
- Deep Learning based spam classification

---

## 👩‍💻 Author

**Navyaa Sharma**

GitHub: https://github.com/Navyaasharma704

LinkedIn: *(Add your LinkedIn profile link here.)*

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

Thank you for visiting this repository!