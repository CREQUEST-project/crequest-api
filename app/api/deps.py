import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel import Session, select
from core.config import settings
from collections.abc import Generator
from core.db import engine
from models.users import User, UserOut
from jose import ExpiredSignatureError, JWTError, jwt
from core import security

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.ROOT_PATH+settings.API_V1_STR}/auth/login"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    This function provides a database session object for use in other functions.

    Parameters:
    None

    Returns:
    Generator[Session, None, None]: A database session object that can be used in other functions.

    Yields:
    Session: A database session object that is yielded for use in other functions.

    Raises:
    None

    Usage:
    The `get_db` function is used to obtain a database session object that can be used in other functions. This session object is then yielded for use in those functions.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> UserOut:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user = session.exec(
            select(User).where(
                User.user_name == payload.get("sub"),
                User.user_role_id == payload.get("user_type"),
            )
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


CurrentUser = Annotated[UserOut, Depends(get_current_user)]
