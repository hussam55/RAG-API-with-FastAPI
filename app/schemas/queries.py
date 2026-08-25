from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True


class Source(BaseModel):
    page: int
    text: str


class AnswerResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    sources: list[Source]
