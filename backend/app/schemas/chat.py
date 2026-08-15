from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def question_no_solo_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La pregunta no puede estar compuesta únicamente de espacios")
        return v


class ChatResponse(BaseModel):
    answer: str