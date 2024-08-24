from sqlmodel import SQLModel


# Generic message
class Message(SQLModel):
    status_code: int
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str | None = None
    token_type: str = "bearer"
    id_token: str | None = None
    refresh_token: str | None = None


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None
