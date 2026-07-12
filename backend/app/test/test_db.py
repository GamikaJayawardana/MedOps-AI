import psycopg

from app.config import settings

print(f"Connecting to: {settings.database_url}")

with psycopg.connect(settings.database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("Connected!")
        