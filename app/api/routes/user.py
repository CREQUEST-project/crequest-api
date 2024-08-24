from fastapi import APIRouter
from api.deps import SessionDep
from models.users import UserOut
from api.deps import CurrentUser

router = APIRouter()

@router.get('/me', response_model=UserOut)
def read_user_me(current_user: CurrentUser) -> UserOut:
    return current_user