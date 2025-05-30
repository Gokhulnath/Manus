import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    MAX_TOKENS_PER_CHUNK = int(os.getenv("MAX_TOKENS_PER_CHUNK"))
    OVERLAPPING_TOKEN = int(os.getenv("OVERLAPPING_TOKEN"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS"))
    PINECONE_CLOUD = os.getenv("PINECONE_CLOUD")
    PINECONE_REGION = os.getenv("PINECONE_REGION")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")

settings = Settings()