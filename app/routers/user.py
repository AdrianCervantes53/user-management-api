from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    description="Creates a new user account. Email must be unique.",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users",
    description="Returns a list of all registered users. Requires authentication.",
)
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_users(db)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get my profile",
    description="Returns the profile of the currently authenticated user.",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "/by-id/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns a user by their UUID.",
)
def get_user(user_id: str, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)
