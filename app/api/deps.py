import logging
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from core.config import settings
from collections.abc import Generator
from core.db import engine

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.ROOT_PATH+settings.API_V1_STR}/login/get-access-token"
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