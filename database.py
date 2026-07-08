from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
FALLBACK_DATABASE_URL = 'postgresql://postgres:3536@localhost:5432/techflow'