from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.deps import SessionDep, get_current_user, verify_user_id
from models.users import ChangePassword, ForgotPassword, UserInfoUpdate, UserOut
from models.base import Message

import api.applications.user.user_controller as UserController


router = APIRouter()


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_user), Depends(verify_user_id)],
    response_model=UserOut,
)
def read_user_info(session: SessionDep, user_id: int) -> UserOut:
    return UserController.read_user_info(session, user_id)


@router.put(
    "/{user_id}",
    dependencies=[Depends(get_current_user), Depends(verify_user_id)],
    response_model=UserOut,
)
def update_user_info(
    session: SessionDep, user_id: int, data_in: UserInfoUpdate
) -> UserOut:
    # validate valid email
    if data_in.email:
        if "@" not in data_in.email:
            raise HTTPException(status_code=400, detail="Invalid email")

    return UserController.update_user_info(session, user_id, data_in)


@router.put(
    "/{user_id}/avatar",
    dependencies=[Depends(get_current_user), Depends(verify_user_id)],
    response_model=UserOut,
)
def update_avatar(
    session: SessionDep, user_id: int, file: UploadFile = File(...)
) -> UserOut:
    return UserController.update_avatar(session, user_id, file)


@router.put(
    "/{user_id}/password/change",
    dependencies=[Depends(get_current_user), Depends(verify_user_id)],
    response_model=UserOut,
)
def change_password(
    session: SessionDep, user_id: int, data_in: ChangePassword
) -> UserOut:
    return UserController.change_password(session, user_id, data_in)


@router.put("/password/forgot", response_model=Message)
def forgot_password(session: SessionDep, data_in: ForgotPassword) -> Message:
    return UserController.forgot_password(session, data_in)
