import base64
from fastapi import File, HTTPException, UploadFile
from sqlmodel import Session, select
from utils import random_password, send_simple_email
from core.security import get_password_hash, verify_password
from models.users import ChangePassword, ForgotPassword, User, UserOut
from models.base import Message
from core.config import settings


def read_user_info(session: Session, user_id: int) -> UserOut:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


def update_user_info(
    session: Session,
    user_id: int,
    email: str,
    location: str,
    phone: str,
    file: UploadFile | None = File(None),
) -> UserOut:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # handle file upload to get base64 image
    if file:
        file_content = file.file.read()
        base64_string = base64.b64encode(file_content).decode("utf-8")
        db_user.avatar = base64_string
        session.flush()
        session.refresh(db_user)

    if email:
        other_user = session.exec(
            select(User).where(User.email == email, User.id != user_id)
        ).first()
        if other_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user.email = email
        session.flush()
        session.refresh(db_user)

    if location:
        db_user.location = location
        session.flush()
        session.refresh(db_user)

    if db_user.phone:
        db_user.phone = phone
        session.flush()
        session.refresh(db_user)

    session.commit()
    session.refresh(db_user)

    return db_user


def change_password(session: Session, user_id: int, data_in: ChangePassword) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if old password is correct
    if not verify_password(data_in.old_password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # change password
    db_user.hashed_password = get_password_hash(data_in.new_password)
    session.commit()
    session.refresh(db_user)

    return db_user


def forgot_password(session: Session, user_id: int, data_in: ForgotPassword) -> Message:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if email is registered
    if db_user.email != data_in.email:
        raise HTTPException(status_code=400, detail="Email not registered")

    # auto generate new password
    new_password = random_password()
    db_user.hashed_password = get_password_hash(new_password)
    session.commit()
    session.refresh(db_user)

    # send new password to email
    send_simple_email(
        [data_in.email],
        "Crequest Forgot Password",
        f"Your new password is: {new_password}",
        settings.EMAIL_HOST_USER,
    )

    return Message(status_code=200, message="New password has been sent to your email")
