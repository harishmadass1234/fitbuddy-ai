import json
from typing import TypeVar

from google import genai
from pydantic import BaseModel

from .config import get_settings


T = TypeVar(
    "T",
    bound=BaseModel,
)


def get_client():

    settings = get_settings()

    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.google_api_key
    )


def generate_structured(
    prompt: str,
    response_model: type[T],
    model_name: str,
) -> T:

    client = get_client()

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": response_model.model_json_schema(),
        },
    )

    text = response.text or ""

    try:

        return response_model.model_validate_json(
            text
        )

    except Exception:

        cleaned = (
            text
            .strip()
            .removeprefix("```json")
            .removesuffix("```")
            .strip()
        )

        return response_model.model_validate(
            json.loads(cleaned)
        )