from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class SearchForCreHistoryBase(SQLModel):
    sequences: str


class SearchForCreHistory(SearchForCreHistoryBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    user: "User" = Relationship(back_populates="search_for_cre_histories")

    class Config:
        from_attributes = True


class SearchForCreHistoryIn(SearchForCreHistoryBase):
    user_id: int


class SearchForCreHistoryOut(SearchForCreHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class SearchForCreHistoryListOut(SQLModel):
    data: list[SearchForCreHistoryOut]
    count: int
