from .config import get_settings
from .gemini_client import generate_structured
from .schemas import (
    DayPlan,
    UserInput,
    WorkoutPlan,
)


DAYS = [
    "Day 1",
    "Day 2",
    "Day 3",
    "Day 4",
    "Day 5",
    "Day 6",
    "Day 7",
]


def fallback_plan(
    data: UserInput,
) -> WorkoutPlan:

    intensity_text = {
        "low": "easy and comfortable",
        "medium": "moderate and manageable",
        "high": "challenging but controlled",
    }[data.intensity]

    focuses = [
        "Full-body movement",
        "Cardio fitness",
        "Lower-body strength",
        "Mobility and flexibility",
        "Upper-body strength",
        "Light cardio and core",
        "Recovery and gentle movement",
    ]

    days = []

    for index, day in enumerate(DAYS):

        if index == 6:

            main = [
                "10–20 minutes of comfortable walking",
                "5–10 minutes of gentle mobility",
            ]

        else:

            main = [
                f"5–10 minutes of {intensity_text} movement",
                "Bodyweight squats: 2 sets of 8–12",
                "Wall or incline push-ups: 2 sets of 6–12",
                "Glute bridges: 2 sets of 8–12",
                "Easy walking: 10–20 minutes",
            ]

        days.append(
            DayPlan(
                day=day,
                focus=focuses[index],
                warmup=(
                    "5–10 minutes of gentle walking "
                    "and dynamic mobility."
                ),
                main_workout=main,
                cooldown=(
                    "5–10 minutes of easy movement "
                    "and relaxed stretching."
                ),
            )
        )

    return WorkoutPlan(
        title=(
            f"FitBuddy 7-Day "
            f"{data.goal.title()} Wellness Plan"
        ),
        safety_note=(
            "This is general wellness guidance, "
            "not medical advice. Adjust activity "
            "to your comfort."
        ),
        days=days,
    )


def generate_workout_gemini(
    data: UserInput,
) -> WorkoutPlan:

    prompt = f"""
Create a safe, age-appropriate 7-day fitness
and wellness plan.

User information:

Age: {data.age}

Goal: {data.goal}

Preferred intensity: {data.intensity}

Weight: {
    data.weight
    if data.weight is not None
    else "not provided"
}

Requirements:

1. Return exactly 7 days.
2. Every day must contain:
   - warm-up
   - main workout
   - cooldown/recovery
3. Explain sets, repetitions or duration.
4. Include at least one lighter recovery day.
5. Keep exercises simple and practical.
6. Do not recommend dangerous challenges.
7. Do not recommend pain-oriented exercise.
8. Do not recommend fasting or extreme dieting.
9. Do not recommend supplements.
10. Do not recommend rapid weight change.
11. Do not diagnose medical conditions.
12. Keep the plan focused on healthy fitness habits.
"""

    try:

        return generate_structured(
            prompt=prompt,
            response_model=WorkoutPlan,
            model_name=(
                get_settings()
                .gemini_workout_model
            ),
        )

    except Exception:

        if get_settings().use_ai_fallback:

            return fallback_plan(data)

        raise