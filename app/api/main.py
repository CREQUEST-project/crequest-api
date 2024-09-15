from fastapi import APIRouter

from api.routes import guest, auth, user, biologist, admin, user_info

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(user_info.router, prefix="/user-info", tags=["user_info"])
api_router.include_router(guest.router, prefix="/guest", tags=["guest"])
api_router.include_router(biologist.router, prefix="/biologist", tags=["biologist"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
