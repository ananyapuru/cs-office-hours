import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load ENV variables
load_dotenv()

# Get DB URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file. Make sure it's set.")
    exit()

# Create a SQLAlchemy engine
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅ Successfully connected to PostgreSQL database!")
except Exception as e:
    print(f"❌ Failed to connect to the database: {e}")
