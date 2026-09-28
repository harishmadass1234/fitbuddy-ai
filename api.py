from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from .database import (
    get_db,
    get_latest_plan,
    get_user,
)

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .schemas import (
    FeedbackRequest,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


router = APIRouter(
    prefix="/api",
    tags=["FitBuddy API"],
)


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "fitbuddy",
    }


@router.post("/generate")
def api_generate(
    data: UserInput,
):

    plan = generate_workout_gemini(
        data
    )

    tip = generate_nutrition_tip_with_flash(
        data
    )

    return {
        "user": data.model_dump(),
        "workout_plan": plan.model_dump(),
        "nutrition_tip": tip,
    }


@router.post("/feedback")
def api_feedback(
    data: FeedbackRequest,

    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        data.user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    plan = get_latest_plan(
        db,
        user,
    )

    if not plan:

        raise HTTPException(
            status_code=404,
            detail="No saved plan for this user.",
        )

    user_input = UserInput(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )

    updated = update_workout_plan(
        plan.original_plan,
        data.feedback,
        user_input,
    )

    return {
        "user_id": user.user_id,
        "updated_plan": updated,
    }