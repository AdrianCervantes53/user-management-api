from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])
    
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_service.login(db, form_data.username, form_data.password)