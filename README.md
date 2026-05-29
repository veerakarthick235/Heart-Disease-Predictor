<div align="center">

# 🫀 CardioPredict AI

### AI-Powered Heart Disease Risk Assessment Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB_Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

A full-stack SaaS web application that uses a **Random Forest machine learning model** to predict cardiovascular disease risk from 13 clinical parameters. Includes a complete authentication system, per-user prediction history, and a premium dark-themed UI.

[Live Demo](#) · [Report Bug](https://github.com/veerakarthick235/Heart-Disease-Predictor/issues) · [Request Feature](https://github.com/veerakarthick235/Heart-Disease-Predictor/issues)

</div>

---

## 📸 Screenshots

| Landing Page | Login | Predictor | History |
|---|---|---|---|
| Public marketing page with hero section, feature cards, and CTA | Two-panel glassmorphism login with live email validation | Protected clinical assessment form with AI result & probability bar | Per-user prediction history with stats cards and risk badges |

---

## ✨ Features

### 🔐 Authentication & Security
- **User Registration** — Full name, email, bcrypt-hashed password (cost factor 12)
- **Secure Login** — Flask-Login session management with persistent cookies
- **Rate Limiting** — 20 req/hr on login, 10 req/hr on register (brute-force protection)
- **Protected Routes** — `@login_required` on all prediction and history endpoints
- **Input Validation** — Server-side regex + client-side real-time feedback
- **Secret Management** — All credentials in `.env`, excluded from version control

### 🤖 AI Prediction Engine
- **Random Forest Classifier** trained on the Cleveland Heart Disease Dataset
- **~85% accuracy** across 13 clinical parameters
- **Probability score** displayed with animated progress bar
- **One-hot encoding** of categorical features matching training pipeline

### 📊 User Dashboard
- **Prediction History** — Table of all assessments with risk badges and probability bars
- **Stats Cards** — Total predictions, high risk count, low risk count, avg probability
- **Profile Page** — Account details, risk distribution bar chart, quick actions
- **Per-user isolation** — Each user only sees their own data

### 🎨 Premium UI
- Dark glassmorphism design with animated gradient backgrounds
- ECG line animation on the landing page hero
- Password strength meter with color-coded levels
- Scroll-reveal animations on feature cards
- Fully responsive (mobile, tablet, desktop)
- Google Fonts (Inter) + Font Awesome icons

---

## 🏗️ Architecture

```
Heart-Disease-Predictor/
│
├── app.py                  # Flask app factory + main routes
├── auth.py                 # Auth blueprint (register/login/logout/profile)
├── config.py               # Configuration class (reads .env)
├── database.py             # MongoDB Atlas connection + collection helpers
├── extensions.py           # Flask extensions (bcrypt, login_manager, limiter)
├── models.py               # User model (Flask-Login + PyMongo)
├── model.py                # ML model training script
├── heart_disease_model.pkl # Trained Random Forest model
├── heart.csv               # Cleveland Heart Disease Dataset
│
├── templates/
│   ├── base.html           # Shared layout (navbar, flash messages, footer)
│   ├── landing.html        # Public marketing page
│   ├── login.html          # Sign-in form
│   ├── register.html       # Sign-up with password strength meter
│   ├── index.html          # Prediction form (protected)
│   ├── history.html        # Prediction history table
│   └── profile.html        # Account info + stats
│
├── static/
│   ├── css/
│   │   ├── auth.css        # Navbar, auth pages, landing, history, profile
│   │   └── style.css       # Prediction form styles
│   └── js/
│       ├── auth.js         # Validation, strength meter, loading states
│       └── script.js       # Prediction form interactions
│
├── .env                    # Secret config (NOT committed to git)
├── .env.example            # Template for environment setup
├── .gitignore              # Protects .env and other artifacts
└── requirements.txt        # Python dependencies
```

---

## 🗄️ Database Schema (MongoDB Atlas)

### `users` collection
```json
{
  "_id":           "ObjectId",
  "full_name":     "Dr. Jane Smith",
  "email":         "jane@example.com",
  "password_hash": "$2b$12$...",
  "created_at":    "ISODate",
  "last_login":    "ISODate",
  "is_active":     true
}
```

### `predictions` collection
```json
{
  "_id":              "ObjectId",
  "user_id":          "ObjectId (ref: users)",
  "inputs":           { "age": "55", "sex": "1", "cp": "2", ... },
  "result":           "POSSIBLE HEART DISEASE",
  "probability":      0.87,
  "prediction_value": 1,
  "created_at":       "ISODate"
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) account (free M0 tier works)
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/veerakarthick235/Heart-Disease-Predictor.git
cd Heart-Disease-Predictor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Flask
FLASK_SECRET_KEY=your-super-secret-flask-key-change-this
FLASK_DEBUG=True

# MongoDB Atlas
# Get this from: Atlas Dashboard → Connect → Drivers → Python
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/heartdisease?retryWrites=true&w=majority
MONGO_DBNAME=heartdisease

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ACCESS_TOKEN_EXPIRES_HOURS=24
```

> **How to get your Atlas URI:**
> 1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)
> 2. Click your cluster → **Connect**
> 3. Choose **Drivers** → **Python**
> 4. Copy the connection string and replace `<password>`

### 4. Train the Model (if needed)

If `heart_disease_model.pkl` is missing:

```bash
python model.py
```

### 5. Run the Application

```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## 🔗 Route Reference

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Public | Landing page |
| `GET/POST` | `/register` | Public | Create account |
| `GET/POST` | `/login` | Public | Sign in |
| `GET` | `/logout` | Required | Sign out |
| `GET/POST` | `/predict` | Required | Run AI prediction |
| `GET` | `/history` | Required | View all predictions |
| `GET` | `/profile` | Required | Account info & stats |

---

## 🧬 Clinical Parameters

The model accepts the following 13 inputs from the Cleveland Heart Disease Dataset:

| Parameter | Description | Range |
|---|---|---|
| `age` | Patient age | 1–120 years |
| `sex` | Biological sex | 0 = Female, 1 = Male |
| `cp` | Chest pain type | 0–3 (Typical Angina → Asymptomatic) |
| `trestbps` | Resting blood pressure | 80–200 mm Hg |
| `chol` | Serum cholesterol | 100–600 mg/dl |
| `fbs` | Fasting blood sugar > 120 mg/dl | 0 = No, 1 = Yes |
| `restecg` | Resting ECG results | 0–2 |
| `thalach` | Maximum heart rate achieved | 70–220 bpm |
| `exang` | Exercise induced angina | 0 = No, 1 = Yes |
| `oldpeak` | ST depression (exercise vs rest) | 0.0–10.0 |
| `slope` | ST segment slope | 0–2 |
| `ca` | Major vessels (fluoroscopy) | 0–3 |
| `thal` | Thalassemia type | 3 = Normal, 6 = Fixed, 7 = Reversible |

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change `FLASK_SECRET_KEY` to a long random string (`python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Change `JWT_SECRET_KEY` similarly
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable HTTPS and set `JWT_COOKIE_SECURE=True` in `config.py`
- [ ] Restrict MongoDB Atlas network access to your server IP
- [ ] Set `JWT_COOKIE_CSRF_PROTECT=True` in production config
- [ ] Use a production WSGI server (`gunicorn app:app`)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.1 |
| **Auth** | Flask-Login, Flask-Bcrypt |
| **Database** | MongoDB Atlas, PyMongo 4.x |
| **Rate Limiting** | Flask-Limiter |
| **ML** | scikit-learn (Random Forest), pandas, numpy, joblib |
| **Frontend** | Vanilla HTML/CSS/JS, Font Awesome 6, Google Fonts (Inter) |
| **Deployment** | Gunicorn (production WSGI) |

---

## ⚠️ Medical Disclaimer

> This application is built for **educational and research purposes only**. The AI predictions are **not a substitute for professional medical diagnosis**. Always consult a qualified healthcare provider for any cardiovascular concerns.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ by [Veera Karthick](https://github.com/veerakarthick235)

</div>
