from fastapi import File, Form, UploadFile
from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel
import uuid
from models.factors_function_labels import FactorsFunctionLabels


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


class Factors(FactorsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ft_id: uuid.UUID | None = Field(
        default=None, nullable=True, foreign_key="factorsfunctionlabels.id"
    )
    factors_function_label: list["FactorsFunctionLabels"] = Relationship(
        back_populates="factors"
    )


class FactorsIn(SQLModel):
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


class FactorsOut(FactorsBase):
    id: uuid.UUID
    function_label: FactorsFunctionLabels | None = None


class FactorsListOut(SQLModel):
    data: list[FactorsOut]
    count: int


class MotifSearch(SQLModel):
    sequence: str


class Position(SQLModel):
    start: int
    end: int


class StrandMatch(SQLModel):
    factor_id: str
    sq: str
    de: str
    function_label: FactorsFunctionLabels | None = None
    positions: list[Position]
    color: str


class MotifSearchOut(SQLModel):
    original_sequence: str
    reverse_complement_sequence: str
    forward_strand_matches: list[StrandMatch]
    reverse_strand_matches: list[StrandMatch]


class MotifSearchAndSaveHistoryOut(MotifSearchOut):
    history_id: int


class QueryCreSearchIn(SQLModel):
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


class MotifSamplerIn(SQLModel):
    f_file: UploadFile
    b_file: UploadFile | None = File(None)
    output_o: str = Form(...)
    output_m: str = Form(...)
    r: int | None = Form(100)
    s: int | None = Form(0)
    w: int | None = Form(8)
    n: int | None = Form(1)
    x: int | None = Form(1)
    M: int | None = Form(2)
    p: int | None = Form(None)
    Q: int | None = Form(100)
    z: int | None = Form(1)


class MotifSamplerResponse(SQLModel):
    status: str
    message: str
    results: list[str] | None = None


class CreResultSendEmail(SQLModel):
    receiver_email: list[str]
    sequence: str


class CreUpdateIn(SQLModel):
    ac: str | None = None
    dt: str | None = None
    de: str | None = None
    kw: str | None = None
    os: str | None = None
    ra: str | None = None
    rt: str | None = None
    rl: str | None = None
    rc: str | None = None
    rd: str | None = None
    sq: str | None = None
    note: str | None = Field(default=None, nullable=True)
    color: str | None = None
