from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import os

db = None

def create_app(config_class=Config):
    global db
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Firebase
    if not firebase_admin._apps:
        cred_path = app.config['FIREBASE_CREDENTIALS']
        if not os.path.exists(cred_path):
            # Try absolute path relative to root if relative path fails
            absolute_path = os.path.join(app.root_path, '..', cred_path)
            if os.path.exists(absolute_path):
                cred_path = absolute_path
        
        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                print(f"Firebase initialized successfully using {cred_path}")
            except Exception as e:
                print(f"Error initializing Firebase: {e}")
                raise e
        else:
            error_msg = f"Firebase credentials file not found at {cred_path} (CWD: {os.getcwd()})"
            print(error_msg)
            raise FileNotFoundError(error_msg)
    else:
         # Already initialized (e.g. valid when using Flask reloader)
         db = firestore.client()

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
