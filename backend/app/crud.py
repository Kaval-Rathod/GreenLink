from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

import models, schemas

# Users

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        wallet_address=user.wallet_address,
    )
    if user.latitude is not None and user.longitude is not None:
        db_user.location = from_shape(Point(user.longitude, user.latitude), srid=4326)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: models.User, data: schemas.UserUpdate):
    if data.name is not None:
        db_user.name = data.name
    if data.wallet_address is not None:
        db_user.wallet_address = data.wallet_address
    if data.latitude is not None and data.longitude is not None:
        db_user.location = from_shape(Point(data.longitude, data.latitude), srid=4326)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()
    return True


# Submissions

def create_submission(db: Session, user_id: int, photo_path: str, latitude: float | None, longitude: float | None):
    submission = models.Submission(user_id=user_id, photo_path=photo_path)
    if latitude is not None and longitude is not None:
        submission.gps_coords = from_shape(Point(longitude, latitude), srid=4326)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_submissions(db: Session, user_id: int | None = None):
    q = db.query(models.Submission)
    if user_id is not None:
        q = q.filter(models.Submission.user_id == user_id)
    return q.order_by(models.Submission.id.desc()).all()


def get_submission(db: Session, submission_id: int):
    return db.query(models.Submission).filter(models.Submission.id == submission_id).first()


def update_submission_analysis(db: Session, submission: models.Submission, greenery_pct: float, carbon_value: float):
    submission.greenery_pct = greenery_pct
    submission.carbon_value = carbon_value
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# Credits

def create_credit(db: Session, user_id: int, tonnes_co2: float, token_id: str | None = None):
    credit = models.Credit(user_id=user_id, tonnes_co2=tonnes_co2, token_id=token_id)
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit


def list_credits(db: Session, user_id: int | None = None):
    q = db.query(models.Credit)
    if user_id is not None:
        q = q.filter(models.Credit.user_id == user_id)
    return q.order_by(models.Credit.id.desc()).all()
