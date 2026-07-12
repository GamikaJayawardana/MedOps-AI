from pinecone import Pinecone

from app.config import settings

# Unwrap the SecretStr to get the raw key string the client expects.
pc = Pinecone(api_key=settings.pinecone_api_key.get_secret_value())

# List existing indexes to confirm the connection works.
indexes = pc.list_indexes()
print("Connection OK. Existing indexes:")
print(indexes)