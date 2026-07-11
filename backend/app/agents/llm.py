from langchain_groq import ChatGroq
from app.config import settings


def get_llm(temperature: float = 0.0) -> ChatGroq:
    # This function returns a ChatGroq instance configured 
    # with the specified temperature and the API key from settings.
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=temperature,
    )