from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
FALLBACK_DATABASE_URL = 'sqlite:///local.db'