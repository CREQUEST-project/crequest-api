from pydantic import field_validator
from sqlmodel import Field, SQLModel
import uuid

class FactorsBase(SQLModel):
    ac: str
    dt: str
    de: str
    kw: str
    os: str
    ra: str
    rt: str
    rl: str
    rc: str
    rd: str
    sq: str
    note: str | None = Field(default=None, nullable=True)
    color: str
    ft_id: uuid.UUID | None = Field(default=None, nullable=True)

class Factors(FactorsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class FactorsIn(FactorsBase):
    pass

class FactorsOut(FactorsBase):
    id: uuid.UUID

class FactorsListOut(SQLModel):
    data: list[FactorsOut]
    count: int

class MotifSearch(SQLModel):
    sequence: str
    
class StrandMatch(SQLModel):
    factor_id: str
    start: int
    end: int
    color: str

class MotifSearchOut(SQLModel):
    original_sequence: str
    reverse_complement_sequence: str
    forward_strand_matches: list[StrandMatch]
    reverse_strand_matches: list[StrandMatch]
    factors: list[FactorsOut]
    
class QueryCareSearchIn(SQLModel):
    id: str | None = None
    ac: str | None = None
    dt: str | None = None
    de: str | None = None
    kw: str | None = None
    os: str | None = None
    ra: str | None = None
    rt: str | None = None
    rl: str | None = None
    rd: str | None = None
    sq: str | None = None
    
    @field_validator("id")
    def check_is_valid_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID")
        return v