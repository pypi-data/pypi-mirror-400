from pydantic import Field, BaseModel

from cheshirecat_python_sdk.models.dtos import MessageBase, Why


class MessageOutput(MessageBase):
    why: Why | None = Field(default_factory=Why)  # Assuming Why has a no-args constructor
    type: str | None = "chat"  # Default argument
    error: bool | None = False  # Default argument


class ChatOutput(BaseModel):
    agent_id: str
    user_id: str
    chat_id: str
    message: MessageOutput
