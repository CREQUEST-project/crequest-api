from datetime import datetime
from sqlmodel import Field, SQLModel


class ComputationalMotifBase(SQLModel):
    sequences: str


class ComputationalMotif(ComputationalMotifBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ComputationalMotifOut(ComputationalMotifBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ComputationalMotifListOut(SQLModel):
    data: list[ComputationalMotifOut]
    count: int

class Sequences(SQLModel):
    sequences: str

class SaveComputationalMotifIn(SQLModel):
    motifs: list[Sequences]