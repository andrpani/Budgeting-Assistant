import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

load_dotenv()

# TODO: add validation for fields like temperature


class ModelConfig(BaseModel):
    name: str
    provider: str
    temperature: float | None = None

class EmbeddingConfig(BaseModel):
    name: str
    provider: str

class Settings(BaseModel):
    model: ModelConfig
    openai_api_key: SecretStr | None = None
    google_genai_api_key: SecretStr | None = None
    huggingface_api_key: SecretStr | None = None
    #db_name: str 


def get_settings(path: str = "config.yaml") -> Settings:
    with open(path, 'r') as configfile:
        data = yaml.safe_load(configfile)
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    google_genai_api_key = os.getenv('GOOGLE_API_KEY')
    huggingface_api_key = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    
    return Settings(
        model = ModelConfig(**data.get('llm', {})),
        openai_api_key=SecretStr(openai_api_key) if openai_api_key else None,
        google_genai_api_key=SecretStr(google_genai_api_key) if google_genai_api_key else None,
        huggingface_api_key=SecretStr(huggingface_api_key) if huggingface_api_key else None
    )