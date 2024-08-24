from datetime import datetime

from sqlmodel import Field, SQLModel

# Shared properties
class UserBase(SQLModel):
    user_name: str = Field(unique=True, index=True)
    user_role_id: int = Field(description="1 = Admin, 2 = User, 3 = Biologist")
    hashed_password: str
    is_active: bool | None = Field(default=True)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)
    
class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserCreate(SQLModel):
    user_name: str
    password: str
    user_role_id: int
    
class UserRegisterResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
