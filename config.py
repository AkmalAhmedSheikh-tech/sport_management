import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')

    # MySQL database configuration
    DB_USER = os.getenv('DB_USER', 'sportsuser')
    DB_PASS = os.getenv('DB_PASS', '')  # set the real value in .env (URL-encode special chars, e.g. @ -> %40)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'sports_league_manager')

    # SQLAlchemy connection string
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
