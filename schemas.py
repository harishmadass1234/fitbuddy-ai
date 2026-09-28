from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


Goal = Literal[
    "general wellness",
    "strength",
    "flexibility",
    "cardio fitness",
    "weight loss",
    "muscle gain",
]

Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    name: str = Field(
        min_length=2,
        max_length=120,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float | None = Field(
        default=None,
        ge=20,
        le=300,
    )

    goal: Goal

    intensity: Intensity

    @field_validator(
        "user_id",
        "name",
    )
    @classmethod
    def clean_text(
        cls,
        value: str,
    ) -> str:

        return " ".join(
            value.strip().split()
        )


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    feedback: str = Field(
        min_length=3,
        max_length=1000,
    )


class DayPlan(BaseModel):

    day: str

    focus: str

    warmup: str

    main_workout: list[str]

    cooldown: str


class WorkoutPlan(BaseModel):

    title: str

    safety_note: str

    days: list[DayPlan]


class TipResponse(BaseModel):

    tip: str