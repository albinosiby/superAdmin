import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    # Path to your Firebase Admin SDK service account key
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS_PATH') or 'serviceAccountKey.json'
