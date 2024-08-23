from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.deps import SessionDep
from models.base import Token
from models.users import UserCreate, UserRegisterResponse

import api.applications.authentication.authentication_controller as AuthenticationController

router = APIRouter()

@router.post('/login', response_model=Token)
def login_get_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return AuthenticationController.login_for_access_token(session, form_data.username, form_data.password)

@router.post('/register', response_model=UserRegisterResponse)
def register_user(session: SessionDep, data_in: UserCreate) -> UserRegisterResponse:
    return AuthenticationController.register_user(session, data_in)