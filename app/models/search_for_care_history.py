from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class SearchForCareHistoryBase(SQLModel):
    sequences: str

class SearchForCareHistory(SearchForCareHistoryBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    user: "User" = Relationship(back_populates="search_for_care_histories")
    
    class Config:
        from_attributes = True

class SearchForCareHistoryIn(SearchForCareHistoryBase):
    user_id: int
    
class SearchForCareHistoryOut(SearchForCareHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime