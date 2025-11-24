from flask import Flask, request, render_template
import joblib
import numpy as np
import pandas as pd
import sys

app = Flask(__name__)

# --- 1. Load the Model and Feature List ---
MODEL_FILENAME = 'heart_disease_model.pkl'
try:
    # Load the dictionary containing both the model and the feature list
    model_metadata = joblib.load(MODEL_FILENAME)
    model = model_metadata['model']
    # The saved features list includes all columns used in training, including one-hot encoded ones
    TRAINING_FEATURES = model_metadata['features'] 
    print("Model and Feature List loaded successfully.")
except FileNotFoundError:
    print(f"ERROR: '{MODEL_FILENAME}' not found. Please run 'model.py' successfully first.")
    sys.exit(1)
except KeyError:
    print(f"ERROR: '{MODEL_FILENAME}' is missing the 'model' or 'features' key. Re-run 'model.py'.")
    sys.exit(1)

# --- 2. Define the expected original input columns (must match model.py EXPECTED_FEATURES) ---
# This list is used to extract data from the HTML form.
ORIGINAL_INPUT_FEATURES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

# --- 3. Helper function for data preprocessing ---
def preprocess_input(data_dict):
    """
    Converts raw form data into the exact format (columns) required by the model.
    """
    
    # 3a. Convert dictionary to a DataFrame for easy manipulation
    # We create a DataFrame with one row using the input dictionary
    input_df = pd.DataFrame([data_dict], columns=ORIGINAL_INPUT_FEATURES)
    
    # Ensure all data is float for numerical processing (except sex for mapping)
    for col in ORIGINAL_INPUT_FEATURES:
        if col != 'sex':
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
    
    # 3b. Handle 'sex' encoding (Mapping text to number if needed, or ensuring 0/1)
    # The form submits a number (1 or 0), but if we were expecting Male/Female strings, 
    # we would encode here. Since the form uses 1/0, we ensure it's treated as a number.
    input_df['sex'] = pd.to_numeric(input_df['sex'], errors='coerce')
    
    # 3c. Apply One-Hot Encoding for categorical features (must match model.py)
    # These columns were converted using get_dummies in model.py.
    # We must do the same here to create the 'thal_6', 'thal_7', 'cp_2', etc., columns.
    CATEGORICAL_COLS = ['cp', 'restecg', 'slope', 'ca', 'thal'] 
    
    # Convert categorical columns to strings before one-hot encoding
    for col in CATEGORICAL_COLS:
        # Convert numeric codes (e.g., 3 for thal) to strings so get_dummies works correctly
        input_df[col] = input_df[col].astype(str)
        
    input_encoded = pd.get_dummies(input_df, columns=CATEGORICAL_COLS, drop_first=False)
    
    # 3d. Align columns with training data
    # Create a structure of zeros with the exact column names the model was trained on
    final_input = pd.DataFrame(0, index=[0], columns=TRAINING_FEATURES)
    
    # Fill in the values from the encoded user input
    for col in input_encoded.columns:
        if col in TRAINING_FEATURES:
            final_input[col] = input_encoded[col].iloc[0]
            
    # The final input must be the numpy array of the aligned DataFrame
    return final_input.values

# --- 4. Define Routes ---

@app.route('/')
def home():
    """Renders the main prediction form page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request from the form."""
    
    # Get data from the form (as a standard dictionary)
    form_data = request.form.to_dict()
    
    try:
        # 4a. Preprocess the raw input data
        input_array = preprocess_input(form_data)
        
        # 4b. Make the prediction
        prediction = model.predict(input_array)[0]
        
        # 4c. Get the prediction probability 
        # Probability of class 1 (heart disease) is at index 1
        probability = model.predict_proba(input_array)[0][1] 
        
        # 4d. Determine result message
        if prediction == 1:
            result = "POSSIBLE HEART DISEASE"
            message = f"Based on the inputs, the model predicts a high risk of heart disease (Probability: {probability*100:.2f}%)."
            color = "#dc3545" # Red
        else:
            result = "NO HEART DISEASE DETECTED"
            # Probability of class 0 is 1 - probability of class 1
            safe_prob = (1 - probability) 
            message = f"Based on the inputs, the model predicts a low risk of heart disease (Probability: {safe_prob*100:.2f}%)."
            color = "#28a745" # Green
            
        return render_template('index.html', 
                               prediction_result=result,
                               prediction_message=message,
                               result_color=color,
                               form_data=form_data) # Pass back data to repopulate form

    except Exception as e:
        error_message = f"A critical error occurred during prediction: {str(e)}. Please check inputs."
        print(f"Prediction Error: {e}")
        return render_template('index.html', error=error_message, form_data=form_data)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)