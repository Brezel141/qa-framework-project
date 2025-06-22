#config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    SQLAlCHEMY_DATABASE_URI = 'sqlite://bugs.db'
    SQLAlCHEMY_TRACK_MODIFICATIONS = False