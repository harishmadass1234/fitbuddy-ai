from datetime import datetime
from typing import Generator

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import get_settings


settings = get_settings()

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    goal: Mapped[str] = mapped_column(
        String(80)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Plan.created_at",
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_pk: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    user: Mapped[User] = relationship(
        back_populates="plans"
    )


def init_db() -> None:
    Base.metadata.create_all(
        bind=engine
    )


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def save_user(
    db: Session,
    user_id: str,
    name: str,
    age: int,
    weight: float | None,
    goal: str,
    intensity: str,
) -> User:

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:

        user.name = name
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity

    else:

        user = User(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        db.add(user)

    db.commit()

    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    original_plan: str,
    nutrition_tip: str,
) -> Plan:

    plan = Plan(
        user_pk=user.id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)

    db.commit()

    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str,
) -> User | None:

    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_latest_plan(
    db: Session,
    user: User,
) -> Plan | None:

    return (
        db.query(Plan)
        .filter(Plan.user_pk == user.id)
        .order_by(Plan.created_at.desc())
        .first()
    )


def update_plan(
    db: Session,
    plan: Plan,
    updated_plan: str,
    feedback: str,
) -> Plan:

    plan.updated_plan = updated_plan

    plan.feedback = feedback

    plan.updated_at = datetime.utcnow()

    db.commit()

    db.refresh(plan)

    return plan


def get_all_users(
    db: Session,
) -> list[User]:

    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


def delete_user(
    db: Session,
    user_id: str,
) -> bool:

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True