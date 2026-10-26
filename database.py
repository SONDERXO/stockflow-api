import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv() # Reads the .env file and makes those values available as environment variables in our Python program.

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from your .env file")

engine = create_engine(DATABASE_URL)