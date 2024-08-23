from datetime import datetime, timedelta
from typing import Any
from core.config import settings
from cryptography.fernet import Fernet
from jose import jwt

ALGORITHM = "HS256"

cipher = Fernet(settings.PW_KEY)

def create_access_token(
    data: str | Any,  # The subject of the token, can be any string
    expires_delta: timedelta,  # The time-to-live of the token, in seconds
) -> str:
    """
    This function creates a JWT (JSON Web Token) access token.

    Args:
    subject (str | Any): The subject of the token, can be any string.
    expires_delta (timedelta): The time-to-live of the token, in seconds.

    Returns:
    str: The encoded JWT access token.

    Raises:
    ValueError: If the `expires_delta` is less than 1 second.

    Usage:
    ```python
    token = create_access_token("user", expires_delta=timedelta(minutes=30))
    ```
    """
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    This function verifies if the given plain password matches the hashed password.

    Args:
    plain_password (str): The plain password to be verified.
    hashed_password (str): The hashed password to be compared with the plain password.

    Returns:
    bool: True if the plain password matches the hashed password, False otherwise.
    """
    return cipher.decrypt(hashed_password.encode()).decode() == plain_password

def get_password_hash(password: str) -> str:
    """
    This function hashes the given password using the bcrypt scheme.

    Args:
    password (str): The password to be hashed.

    Returns:
    str: The hashed password.
    """
    return cipher.encrypt(password.encode()).decode()


def get_password_plain(hashed_password: str) -> str:
    """
    This function decrypts the given hashed password.

    Args:
    hashed_password (str): The hashed password to be decrypted.

    Returns:
    str: The decrypted password.
    """
    return cipher.decrypt(hashed_password.encode()).decode()