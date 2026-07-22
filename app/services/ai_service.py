import logging
from dataclasses import dataclass
from typing import Dict, Optional

from app.infrastructure.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    provider: str
    status: str
    category: str
    sentiment: str
    priority: str
    summary: str
    suggested_reply: str
    fallback_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, str | None]:
        return {
            "provider": self.provider,
            "status": self.status,
            "category": self.category,
            "sentiment": self.sentiment,
            "priority": self.priority,
            "summary": self.summary,
            "suggested_reply": self.suggested_reply,
            "fallback_reason": self.fallback_reason,
        }


class AIService:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    async def analyze(self, *, name: str, email: str, comment: str) -> AIAnalysisResult:
        try:
            payload = await self.client.analyze_comment(name=name, email=email, comment=comment)
            return AIAnalysisResult(
                provider=payload.get("provider", "openai"),
                status=payload.get("status", "success"),
                category=payload["category"],
                sentiment=payload["sentiment"],
                priority=payload["priority"],
                summary=payload["summary"],
                suggested_reply=payload["suggested_reply"],
            )
        except Exception as exc:
            logger.warning("AI fallback used: %s", exc)
            return self._fallback(comment=comment)

    def _fallback(self, *, comment: str) -> AIAnalysisResult:
        text = comment.lower()
        category = "general"
        priority = "low"
        sentiment = "neutral"

        if any(word in text for word in ["работ", "ваканс", "hire", "job"]):
            category = "job_offer"
            priority = "medium"
        elif any(word in text for word in ["проект", "заказ", "site", "landing", "app"]):
            category = "project_request"
            priority = "high"
        elif any(word in text for word in ["ошиб", "не работает", "bug", "support"]):
            category = "support"
            priority = "high"

        if any(word in text for word in ["спасибо", "great", "awesome", "nice"]):
            sentiment = "positive"
        elif any(word in text for word in ["плохо", "problem", "issue", "плохо"]):
            sentiment = "negative"

        summary = comment[:180].strip()
        suggested_reply = "Спасибо за обращение. Мы изучим запрос и вернемся с ответом в ближайшее время."

        return AIAnalysisResult(
            provider="fallback",
            status="fallback",
            category=category,
            sentiment=sentiment,
            priority=priority,
            summary=summary,
            suggested_reply=suggested_reply,
            fallback_reason="AI provider unavailable or request failed",
        )

