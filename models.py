"""
models.py — User model compatible with Flask-Login.
Works with MongoDB (no ORM — pure PyMongo).
"""

from datetime import datetime, timezone
from bson import ObjectId
from flask_login import UserMixin
from database import users_col, predictions_col
from extensions import bcrypt


class User(UserMixin):
    """
    Flask-Login compatible User class backed by MongoDB.
    Instances are created from MongoDB documents.
    """

    def __init__(self, user_doc):
        self._id = str(user_doc['_id'])
        self.email = user_doc['email']
        self.full_name = user_doc.get('full_name', '')
        self.password_hash = user_doc.get('password_hash', '')
        self.created_at = user_doc.get('created_at', datetime.now(timezone.utc))
        self.last_login = user_doc.get('last_login')
        self.is_active_account = user_doc.get('is_active', True)

    # --- Flask-Login required interface ---

    def get_id(self):
        return self._id

    @property
    def is_active(self):
        return self.is_active_account

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # --- Password helpers ---

    def check_password(self, plain_password):
        """Verify a plain-text password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    # --- Class-level factory methods ---

    @classmethod
    def get_by_id(cls, user_id):
        """Load a user from MongoDB by their string ID."""
        try:
            doc = users_col().find_one({'_id': ObjectId(user_id)})
            return cls(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def get_by_email(cls, email):
        """Load a user from MongoDB by email address."""
        doc = users_col().find_one({'email': email.lower().strip()})
        return cls(doc) if doc else None

    @classmethod
    def create(cls, full_name, email, password):
        """
        Register a new user.
        Returns (User, None) on success or (None, error_message) on failure.
        """
        email = email.lower().strip()

        # Check for duplicate email
        if users_col().find_one({'email': email}):
            return None, 'An account with this email already exists.'

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        now = datetime.now(timezone.utc)

        doc = {
            'full_name': full_name.strip(),
            'email': email,
            'password_hash': password_hash,
            'created_at': now,
            'last_login': now,
            'is_active': True,
        }

        result = users_col().insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls(doc), None

    def update_last_login(self):
        """Record the login timestamp in MongoDB."""
        now = datetime.now(timezone.utc)
        users_col().update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'last_login': now}}
        )
        self.last_login = now

    # --- Prediction helpers ---

    def save_prediction(self, inputs, result, probability, prediction_value):
        """Persist a prediction result for this user."""
        doc = {
            'user_id': ObjectId(self._id),
            'inputs': inputs,
            'result': result,
            'probability': round(float(probability), 4),
            'prediction_value': int(prediction_value),
            'created_at': datetime.now(timezone.utc),
        }
        predictions_col().insert_one(doc)

    def get_predictions(self, limit=50):
        """Return this user's prediction history, newest first."""
        cursor = predictions_col().find(
            {'user_id': ObjectId(self._id)},
            sort=[('created_at', -1)],
            limit=limit
        )
        return list(cursor)

    def get_prediction_stats(self):
        """Return summary stats for the user's predictions."""
        preds = self.get_predictions(limit=1000)
        total = len(preds)
        if total == 0:
            return {'total': 0, 'high_risk': 0, 'low_risk': 0, 'avg_probability': 0}
        high_risk = sum(1 for p in preds if p['prediction_value'] == 1)
        avg_prob = sum(p['probability'] for p in preds) / total
        return {
            'total': total,
            'high_risk': high_risk,
            'low_risk': total - high_risk,
            'avg_probability': round(avg_prob * 100, 1),
        }

    def __repr__(self):
        return f'<User {self.email}>'
