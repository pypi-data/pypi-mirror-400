from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


def get_model(api_key: str) -> BaseChatModel:
    return ChatOpenAI(
        model="google/gemini-2.5-flash",
        base_url="https://openrouter.ai/api/v1",
        api_key=lambda: api_key,
        reasoning_effort="medium"
    )
