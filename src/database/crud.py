from sqlalchemy.orm import Session
from src.database import models
from src.api.schemas.paper import PaperCreate
from src.api.schemas.user import UserCreate
from typing import List, Optional

def create_paper(db: Session, paper: PaperCreate) -> models.Paper:
    db_paper = models.Paper(
        title=paper.title,
        abstract=paper.abstract,
        content=paper.content if hasattr(paper, "content") else None
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

def get_paper_by_id(db: Session, paper_id: int) -> Optional[models.Paper]:
    return db.query(models.Paper).filter(models.Paper.id == paper_id).first()

def get_all_papers(db: Session) -> List[models.Paper]:
    return db.query(models.Paper).all()

def create_user(db: Session, user: UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()
