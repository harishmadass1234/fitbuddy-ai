from .config import get_settings
from .gemini_client import generate_structured
from .gemini_generator import fallback_plan
from .schemas import (
    UserInput,
    WorkoutPlan,
)


def update_workout_plan(
    original_plan: str,
    feedback: str,
    data: UserInput,
) -> str:

    prompt = f"""
Revise the existing 7-day fitness plan using
the user's feedback.

User goal:
{data.goal}

Intensity:
{data.intensity}

Age:
{data.age}

Feedback:
{feedback}

Existing plan:
{original_plan}

Return a complete replacement 7-day plan.

Requirements:

- exactly 7 days
- warm-up each day
- main workout each day
- cooldown/recovery each day
- at least one lighter/recovery day
- safe and age-appropriate
- no dangerous challenges
- no pain-oriented exercise
- no fasting
- no calorie restriction
- no supplements
- no rapid weight-change advice
"""

    try:

        plan = generate_structured(
            prompt=prompt,
            response_model=WorkoutPlan,
            model_name=(
                get_settings()
                .gemini_workout_model
            ),
        )

        return plan.model_dump_json(
            indent=2
        )

    except Exception:

        if get_settings().use_ai_fallback:

            plan = fallback_plan(data)

            return plan.model_dump_json(
                indent=2
            )

        raise