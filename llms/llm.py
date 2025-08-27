from utils.config import get_settings
from langchain_google_genai import ChatGoogleGenerativeAI

settings = get_settings()

def get_llm():
    if settings.model.provider == 'OpenAI':
        pass
    elif settings.model.provider == 'google_genai':
        return ChatGoogleGenerativeAI(
            model=settings.model.name,
            temperature=settings.model.temperature
        )