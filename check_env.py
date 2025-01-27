import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    print(f"DATABASE_URL loaded successfully: {DATABASE_URL}")
else:
    print("DATABASE_URL is not set. Check your .env file.")