from pydantic_settings import BaseSettings
import pyodbc
import os
from typing import Optional

class Settings(BaseSettings):
    # Database 1 (existing)
    HOST: Optional[str] = os.environ.get("HOST", "localhost")
    USER: Optional[str] = os.environ.get("USER", "user")
    PASSWORD: Optional[str] = os.environ.get("PASSWORD", "password")
    DB: Optional[str] = os.environ.get("DB", "database")

    # Database 2 (new variables for DB2)
    HOST_76: Optional[str] = os.environ.get("HOST_76", "localhost")
    USER_76: Optional[str] = os.environ.get("USER_76", "user")
    PASSWORD_76: Optional[str] = os.environ.get("PASSWORD_76", "password")
    DB_76: Optional[str] = os.environ.get("DB_76", "database")

    SECRET_KEY: str = "veryImportantInformation"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = "app/core/.env"  # path to your .env file
        env_file_encoding = 'utf-8'
        case_sensitive = True

# Initialize settings
settings = Settings()


def get_db_connection(db_name="testing"):
    """Connect to either DB1 or DB2 based on the `db_name` argument."""
    
    if db_name == "testing":
        host = settings.HOST
        user = settings.USER
        password = settings.PASSWORD
        db = settings.DB
    elif db_name == "NJ76":
        host = settings.HOST_76
        user = settings.USER_76
        password = settings.PASSWORD_76
        db = settings.DB_76
    else:
        raise ValueError("Invalid database name. Use 'testing' or 'NJ76'.")
    
    try:
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host};"
            f"DATABASE={db};"
            f"UID={user};"
            f"PWD={password}"
        )
        return connection
    except pyodbc.Error as e:
        raise Exception(f"Database connection error: {e}")
