import json
import os
from pydantic import BaseModel, Field

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class LLMSettings(BaseModel):
    provider: str = Field(default="ollama")
    primary_model: str = Field(default="gpt-oss:120b-cloud")
    secondary_model: str = Field(default="minimax-m2:cloud")
    reasoning_model: str = Field(default="deepseek-v3.1:671b-cloud")
    fast_reasoning_model: str = Field(default="glm-4.6:cloud")
    coder_model: str = Field(default="deepseek-v3.1:671b-cloud")
    temperature: float = Field(default=0.0)
    base_url: str = Field(default="http://localhost:11434")
    timeout: int = Field(default=120)

class ExecutionSettings(BaseModel):
    default_timeout: int = Field(default=300)

class Settings(BaseModel):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)

def load_settings() -> Settings:
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r") as f:
                data = json.load(f)
                return Settings(**data)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}. Using defaults.")
    return Settings()

settings = load_settings()
