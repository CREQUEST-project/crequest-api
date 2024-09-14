from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from models.search_for_cre_history import SearchForCreHistory


# Shared properties
class UserBase(SQLModel):
    user_name: str = Field(unique=True, index=True)
    user_role_id: int = Field(description="1 = Admin, 2 = User, 3 = Biologist")
    hashed_password: str
    is_active: bool | None = Field(default=True)
    email: str | None = Field(default=None)
    location: str | None = Field(default=None, nullable=True)
    phone: str | None = Field(default=None, nullable=True)
    avatar: str | None = Field(default=None, nullable=True)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)
    search_for_cre_histories: list["SearchForCreHistory"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserCreate(SQLModel):
    user_name: str
    password: str
    user_role_id: int
    email: str


class UserRegisterResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserInfoUpdate(SQLModel):
    email: str | None
    location: str | None
    phone: str | None


class ChangePassword(SQLModel):
    old_password: str
    new_password: str


class ForgotPassword(SQLModel):
    email: str
