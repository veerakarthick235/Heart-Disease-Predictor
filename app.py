"""
app.py — Main Flask Application (SaaS Enhanced)
Heart Disease Predictor with MongoDB Atlas auth backend.
"""

import sys
import os
from datetime import datetime, timezone

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from config import Config
from extensions import bcrypt, login_manager, limiter
from database import test_connection
from models import User
from auth import auth

# ─────────────────────────────────────────────
# App Factory
# ─────────────────────────────────────────────

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Flask-Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access CardioPredict AI.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    app.register_blueprint(auth)

    return app


app = create_app()


# ─────────────────────────────────────────────
# Flask-Login User Loader
# ─────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# ─────────────────────────────────────────────
# Load ML Model
# ─────────────────────────────────────────────

MODEL_FILENAME = 'heart_disease_model.pkl'
try:
    model_metadata = joblib.load(MODEL_FILENAME)
    model = model_metadata['model']
    TRAINING_FEATURES = model_metadata['features']
    print("[OK] ML Model loaded successfully.")
except FileNotFoundError:
    print(f"[ERROR] '{MODEL_FILENAME}' not found. Run 'model.py' first.")
    sys.exit(1)
except KeyError:
    print(f"[ERROR] '{MODEL_FILENAME}' missing keys. Re-run 'model.py'.")
    sys.exit(1)

ORIGINAL_INPUT_FEATURES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]


# ─────────────────────────────────────────────
# Preprocessing
# ─────────────────────────────────────────────

def preprocess_input(data_dict):
    """Convert raw form data into the feature vector expected by the model."""
    input_df = pd.DataFrame([data_dict], columns=ORIGINAL_INPUT_FEATURES)

    for col in ORIGINAL_INPUT_FEATURES:
        if col != 'sex':
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
    input_df['sex'] = pd.to_numeric(input_df['sex'], errors='coerce')

    CATEGORICAL_COLS = ['cp', 'restecg', 'slope', 'ca', 'thal']
    for col in CATEGORICAL_COLS:
        input_df[col] = input_df[col].astype(str)

    input_encoded = pd.get_dummies(input_df, columns=CATEGORICAL_COLS, drop_first=False)
    final_input = pd.DataFrame(0, index=[0], columns=TRAINING_FEATURES)
    for col in input_encoded.columns:
        if col in TRAINING_FEATURES:
            final_input[col] = input_encoded[col].iloc[0]

    return final_input.values


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """Public landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('predict_page'))
    return render_template('landing.html')


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict_page():
    """Main prediction form (GET) and prediction handler (POST)."""
    if request.method == 'GET':
        return render_template('index.html')

    # POST — run prediction
    form_data = request.form.to_dict()
    try:
        input_array = preprocess_input(form_data)
        prediction = model.predict(input_array)[0]
        probability = model.predict_proba(input_array)[0][1]

        if prediction == 1:
            result = "POSSIBLE HEART DISEASE"
            message = (
                f"Based on the inputs, the model predicts a HIGH risk of heart disease "
                f"(Probability: {probability * 100:.2f}%)."
            )
            color = "#ef4444"
        else:
            safe_prob = 1 - probability
            result = "NO HEART DISEASE DETECTED"
            message = (
                f"Based on the inputs, the model predicts a LOW risk of heart disease "
                f"(Probability: {safe_prob * 100:.2f}%)."
            )
            color = "#22c55e"

        # Save prediction to MongoDB
        current_user.save_prediction(
            inputs=form_data,
            result=result,
            probability=probability if prediction == 1 else (1 - probability),
            prediction_value=int(prediction),
        )

        return render_template(
            'index.html',
            prediction_result=result,
            prediction_message=message,
            result_color=color,
            form_data=form_data,
            probability=round(probability * 100 if prediction == 1 else (1 - probability) * 100, 2),
        )

    except Exception as e:
        error_message = f"An error occurred during prediction: {str(e)}. Please check your inputs."
        print(f"Prediction Error: {e}")
        return render_template('index.html', error=error_message, form_data=form_data)


@app.route('/history')
@login_required
def history():
    """User's prediction history page."""
    predictions = current_user.get_predictions(limit=50)
    stats = current_user.get_prediction_stats()
    return render_template('history.html', predictions=predictions, stats=stats)


# ─────────────────────────────────────────────
# Template Filters
# ─────────────────────────────────────────────

@app.template_filter('format_date')
def format_date(dt):
    """Format a datetime for display."""
    if dt is None:
        return 'N/A'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime('%b %d, %Y at %I:%M %p UTC')


@app.template_filter('format_date_short')
def format_date_short(dt):
    if dt is None:
        return 'N/A'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime('%b %d, %Y')


# ─────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────

if __name__ == '__main__':
    print("[*] Starting CardioPredict AI...")
    print("=" * 50)
    
    # Test MongoDB connection (non-fatal in dev mode)
    db_ok = test_connection()
    if not db_ok:
        print("[!] MongoDB not connected. Auth features will not work.")
        print("    Update MONGO_URI in your .env file to connect to Atlas.")
    
    print("=" * 50)
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)