from datetime import timedelta
from sqlmodel import Session, select
from models.base import Token
from models.users import User, UserCreate, UserRegisterResponse
from core.security import verify_password, create_access_token, get_password_hash
from core.config import settings
from fastapi import HTTPException

def login_for_access_token(session: Session, user_name: str, password: str) -> Token | None:
    db_user = session.exec(select(User).where(User.user_name == user_name)).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.user_name, "user_type": db_user.user_role_id},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token, refresh_token=access_token, token_type="bearer"
    )
    
def register_user(session: Session, data_in: UserCreate) -> UserRegisterResponse:
    """
    Registers a user by their email address, password and username.

    Args:
        session (Session): The SQLAlchemy session object.

    Returns:
        User | None: The registered user object if successful, otherwise None.
    """
    hashed_password = get_password_hash(data_in.password)

    # check is user_name already exist
    user = session.exec(select(User).where(User.user_name == data_in.user_name)).first()
    if user:
        raise HTTPException(status_code=400, detail="User name already registered")

    valid_user_roles = [2, 3]
    
    if data_in.user_role_id not in valid_user_roles:
        raise HTTPException(status_code=400, detail="Invalid user role ID")
    
    user = User(
        user_name=data_in.user_name,
        user_role_id=data_in.user_role_id,
        hashed_password=hashed_password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user