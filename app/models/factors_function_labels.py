from datetime import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel


class FactorsFunctionLabelsBase(SQLModel):
    label: str
    detail_label: str


class FactorsFunctionLabels(FactorsFunctionLabelsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)

    factors: "Factors" = Relationship(
        back_populates="factors_function_label",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )

    class Config:
        from_attributes: bool = True
