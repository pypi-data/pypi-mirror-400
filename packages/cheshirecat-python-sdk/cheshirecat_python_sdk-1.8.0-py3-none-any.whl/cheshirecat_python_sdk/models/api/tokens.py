from pydantic import BaseModel


class TokenOutput(BaseModel):
    access_token: str
    token_type: str | None = "bearer"


class User(BaseModel):
    id: str
    username: str
    permissions: dict[str, list[str]]
    created_at: float | None = None
    updated_at: float | None = None


class AgentMatch(BaseModel):
    agent_name: str
    user: User


class MeOutput(BaseModel):
    success : bool
    agents: list[AgentMatch]
    auto_selected: bool
