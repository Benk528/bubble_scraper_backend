from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing in the environment variables.")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """Initializes the Supabase database by checking for existing data."""
    try:
        response = supabase.table("scrapes").select("*").execute()
        if not response.data:
            supabase.table("scrapes").insert({
                "page_title": "Test Title",
                "meta_data": {},
                "headings": [],
                "paragraphs": [],
                "links": [],
                "images": []
            }).execute()
            print("Test data inserted into scrapes table.")
        else:
            print("Database already initialized.")
    except Exception as e:
        print(f"Error initializing database: {e}")

def save_scrape(data):
    """Saves the scraped data to the Supabase database."""
    response = supabase.table("scrapes").insert(data).execute()
    return response

def get_all_scrapes():
    """Retrieves all scraped data from the Supabase database."""
    response = supabase.table("scrapes").select("*").execute()
    return response.data

def get_scrapes_by_user(user_id):
    """Retrieves all scraped data for a specific user from Supabase."""
    response = supabase.table("scrapes").select("*").eq("user_id", user_id).execute()
    return response.data