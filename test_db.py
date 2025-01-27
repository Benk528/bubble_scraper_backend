from database import get_connection

print("Starting database test...")

conn = get_connection()
if conn:
    print("Connection to PostgreSQL is successful!")
else:
    print("Failed to connect to PostgreSQL.")