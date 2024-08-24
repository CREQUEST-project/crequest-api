from fastapi import APIRouter

from api.routes import guest, auth, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(guest.router, prefix="/guest", tags=["guest"])
