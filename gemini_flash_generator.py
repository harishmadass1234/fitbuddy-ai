from .config import get_settings
from .gemini_client import generate_structured
from .schemas import (
    TipResponse,
    UserInput,
)


def fallback_tip(
    data: UserInput,
) -> str:

    if data.goal == "muscle gain":

        return (
            "Choose regular balanced meals and "
            "include a protein source such as "
            "beans, eggs, dairy, fish or chicken. "
            "Hydration and sleep also support recovery."
        )

    if data.goal == "weight loss":

        return (
            "Focus on regular balanced meals, "
            "fruits and vegetables, hydration, "
            "sleep and enjoyable physical activity "
            "rather than restrictive dieting."
        )

    if data.goal == "flexibility":

        return (
            "Stay hydrated and include gentle "
            "mobility work after warming up. "
            "Move comfortably rather than forcing "
            "a stretch."
        )

    return (
        "Prioritize regular balanced meals, "
        "hydration, adequate sleep and enjoyable "
        "physical activity to support overall wellness."
    )


def generate_nutrition_tip_with_flash(
    data: UserInput,
) -> str:

    prompt = f"""
Give one concise nutrition or recovery tip.

Goal:
{data.goal}

Workout intensity:
{data.intensity}

The tip should:

- be practical
- support healthy habits
- mention balanced food, hydration or recovery
  when appropriate
- avoid calorie counting
- avoid restrictive dieting
- avoid supplements
- avoid extreme weight-loss advice
- be one short paragraph
"""

    try:

        result = generate_structured(
            prompt=prompt,
            response_model=TipResponse,
            model_name=(
                get_settings()
                .gemini_tip_model
            ),
        )

        return result.tip

    except Exception:

        if get_settings().use_ai_fallback:

            return fallback_tip(data)

        raise