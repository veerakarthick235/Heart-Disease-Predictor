import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib # To save/load the model
import sys # For clean exiting
import numpy as np # For numerical checks

# --- 1. Define Expected Features and Common Alternatives ---
EXPECTED_FEATURES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]
TARGET_FEATURE = 'target'

# Mapping of common alternative names to the expected standard name
# FIXED: 'thalch' is added for thalach, and 'num' for target based on your data.
COL_MAPPING = {
    'thalach': ['thalachh', 'max_hr', 'max_heart_rate', 'thalch'],
    'trestbps': ['bp', 'resting_bp', 'blood_pressure'],
    'chol': ['cholesterol', 'serum_chol'],
    'cp': ['chest_pain_type'],
    'target': ['output', 'num', 'diagnosis']
}

# --- 2. Load the dataset ---
try:
    data = pd.read_csv('heart.csv')
    print("Dataset 'heart.csv' loaded successfully.")
except FileNotFoundError:
    print("ERROR: 'heart.csv' not found. Please download the UCI Heart Disease dataset and place it in the project folder.")
    sys.exit(1)


# --- 3. Feature Validation and Mapping (Renaming columns to standard) ---

# 3a. Find and map target column
actual_target = None
if TARGET_FEATURE in data.columns:
    actual_target = TARGET_FEATURE
else:
    for alt_name in COL_MAPPING.get(TARGET_FEATURE, []):
        if alt_name in data.columns:
            actual_target = alt_name
            break

if not actual_target:
    print(f"ERROR: Could not find the target column ('{TARGET_FEATURE}' or alternatives) in the dataset.")
    sys.exit(1)
if actual_target != TARGET_FEATURE:
    data = data.rename(columns={actual_target: TARGET_FEATURE})
    print(f"Mapped target column from '{actual_target}' to '{TARGET_FEATURE}'.")


# 3b. Validate and map all feature columns
final_features = []
missing_features = []

for expected_col in EXPECTED_FEATURES:
    if expected_col in data.columns:
        final_features.append(expected_col)
    else:
        found_alt = False
        for alt_name in COL_MAPPING.get(expected_col, []):
            if alt_name in data.columns:
                data = data.rename(columns={alt_name: expected_col})
                final_features.append(expected_col)
                print(f"Mapped feature column from '{alt_name}' to '{expected_col}'.")
                found_alt = True
                break
        if not found_alt:
            missing_features.append(expected_col)

if missing_features:
    print("\nFATAL ERROR: The following required feature columns are still missing:")
    print(missing_features)
    sys.exit(1)


# --- 4. Data Cleaning and Encoding (FIX for ValueError: could not convert string to float) ---
print("\nStarting data cleaning and encoding...")

# Identify object (string) columns based on feature names
# Common string columns: 'sex', 'cp', 'restecg', 'slope', 'ca', 'thal'
string_cols = data.select_dtypes(include=['object']).columns

# --- Handling the 'sex' column (Male/Female) ---
if 'sex' in string_cols:
    # Use standard pandas encoding for binary features (1 for Male, 0 for Female is common)
    data['sex'] = data['sex'].replace({'Male': 1, 'Female': 0, 'M': 1, 'F': 0})
    print("Encoded 'sex' column (Male=1, Female=0).")

# --- Handling other potential string columns ('thal', 'cp', etc.) ---
# Using pandas 'get_dummies' for One-Hot Encoding on any remaining categorical string columns.
# This creates new binary columns for each unique string value (e.g., thal_normal, thal_fixed defect).
data = pd.get_dummies(data, columns=string_cols, drop_first=True)
print("Applied One-Hot Encoding to remaining categorical columns.")

# --- 5. Prepare Data (Feature Selection and Target) ---
# We must now update final_features to include the new one-hot encoded columns
initial_features = final_features
final_features = [col for col in data.columns if col in initial_features or col.startswith('thal_') or col.startswith('cp_')]

X = data[[col for col in final_features if col != TARGET_FEATURE]]
y = data[TARGET_FEATURE]

# Drop rows with any non-numerical values (e.g., '?' or true NaN left after mapping)
X = X.replace('?', np.nan).dropna()
y = y[X.index] 

print(f"\nTraining model with {len(X)} records and {len(X.columns)} features.")

# --- 6. Split Data ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 7. Train the Model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- 8. Evaluate the Model ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy*100:.2f}%")

# --- 9. Save the Trained Model ---
# We need to save the final list of features (including the encoded ones) used during training.
# This ensures the Flask app uses the exact same input structure for prediction.
model_metadata = {
    'model': model,
    'features': list(X.columns) # Save the list of feature columns
}

MODEL_FILENAME = 'heart_disease_model.pkl'
joblib.dump(model_metadata, MODEL_FILENAME)
print(f"Model and feature list saved as '{MODEL_FILENAME}'")