from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password, create_access_token
from app.models import User


def login(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}