import json
import secrets

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .config import get_settings

from .database import (
    delete_user,
    get_all_users,
    get_db,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
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


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


def is_admin(
    token: str | None,
) -> bool:

    configured_token = (
        get_settings().admin_token
    )

    return (
        bool(token)
        and secrets.compare_digest(
            token,
            configured_token,
        )
    )


def parse_plan(
    plan_text: str,
):

    try:

        return json.loads(
            plan_text
        )

    except Exception:

        return plan_text


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,

    user_id: str = Form(...),

    name: str = Form(...),

    age: int = Form(...),

    weight: float | None = Form(None),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        user = save_user(
            db,
            **data.model_dump(),
        )

        plan = generate_workout_gemini(
            data
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data
            )
        )

        plan_record = save_plan(
            db,
            user,
            plan.model_dump_json(
                indent=2
            ),
            nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": parse_plan(
                    plan_record.original_plan
                ),
                "nutrition_tip": nutrition_tip,
                "plan_id": plan_record.id,
                "message": None,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "message": str(exc)
            },
            status_code=500,
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        request_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            request_data.user_id,
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
                detail="No workout plan found.",
            )

        data = UserInput(
            user_id=user.user_id,
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        updated = update_workout_plan(
            plan.original_plan,
            request_data.feedback,
            data,
        )

        update_plan(
            db,
            plan,
            updated,
            request_data.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": parse_plan(
                    updated
                ),
                "original_plan": parse_plan(
                    plan.original_plan
                ),
                "nutrition_tip": (
                    plan.nutrition_tip
                ),
                "plan_id": plan.id,
                "message": (
                    "Your plan was updated "
                    "using your feedback."
                ),
            },
        )

    except HTTPException as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "message": exc.detail
            },
            status_code=exc.status_code,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "message": str(exc)
            },
            status_code=500,
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,

    token: str | None = None,

    db: Session = Depends(get_db),
):

    if not is_admin(token):

        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "message": (
                    "Enter the admin token "
                    "configured in your .env file."
                )
            },
            status_code=401,
        )

    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "token": token,
        },
    )


@router.post(
    "/admin/delete/{user_id}"
)
def admin_delete_user(
    user_id: str,

    token: str = Form(...),

    db: Session = Depends(get_db),
):

    if not is_admin(token):

        raise HTTPException(
            status_code=401,
            detail="Invalid admin token.",
        )

    delete_user(
        db,
        user_id,
    )

    return RedirectResponse(
        url=(
            "/view-all-users"
            f"?token={token}"
        ),
        status_code=303,
    )