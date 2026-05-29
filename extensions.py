"""
extensions.py — Initialize Flask extensions (without app context).
These are imported by app.py and auth.py to avoid circular imports.
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bcrypt = Bcrypt()

login_manager = LoginManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
