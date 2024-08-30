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