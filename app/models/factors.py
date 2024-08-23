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