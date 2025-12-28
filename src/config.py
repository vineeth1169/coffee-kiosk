import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'devsecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_uri():
        """Return the DB URI.

        Priority:
        1. SQLALCHEMY_DATABASE_URI env var
        2. MySQL if MYSQL_* env vars are set
        3. Fallback to local SQLite file `dev.db`
        """
        uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if uri:
            return uri

        # If MySQL-specific env vars are present, construct a MySQL URI
        mysql_user = os.getenv('MYSQL_USER')
        mysql_db = os.getenv('MYSQL_DB')
        if mysql_user or mysql_db:
            user = os.getenv('MYSQL_USER', 'root')
            password = os.getenv('MYSQL_PASSWORD', '')
            host = os.getenv('MYSQL_HOST', '127.0.0.1')
            port = os.getenv('MYSQL_PORT', '3306')
            db = os.getenv('MYSQL_DB', 'coffee_kiosk')
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

        # Default to a local sqlite database file for easy development
        return os.getenv('SQLITE_DATABASE_URI', 'sqlite:///dev.db')

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
