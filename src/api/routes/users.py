from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database import crud
from src.api.schemas.user import User, UserCreate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken.")

    db_user = crud.create_user(db, user)
    return db_user
