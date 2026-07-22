from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    provider: str = Field(..., examples=["openai", "fallback"])
    status: str = Field(..., examples=["success", "fallback"])
    category: str = Field(..., examples=["job_offer", "project_request", "general"])
    sentiment: str = Field(..., examples=["positive", "neutral", "negative"])
    priority: str = Field(..., examples=["low", "medium", "high"])
    summary: str
    suggested_reply: str
    fallback_reason: str | None = None

