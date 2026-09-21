from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.metrics import WorkspaceView


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)

    @field_validator("question")
    @classmethod
    def question_no_solo_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La pregunta no puede estar compuesta únicamente de espacios")
        return v

    @field_validator("history")
    @classmethod
    def history_contenido_texto(cls, history: list[HistoryMessage]) -> list[HistoryMessage]:
        cleaned: list[HistoryMessage] = []
        for item in history:
            content = item.content.strip()
            if not content:
                continue
            cleaned.append(HistoryMessage(role=item.role, content=content[:2000]))
        return cleaned


class ChatResponse(BaseModel):
    answer: str
    tools: list["ToolResult"] = []
    view: Optional[WorkspaceView] = None


class ToolResult(BaseModel):
    name: str
    arguments: dict = {}
    result: Optional[dict | list | int | float | str] = None
    sql: Optional[str] = None
