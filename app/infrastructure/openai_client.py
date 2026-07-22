import logging
from typing import Any, Dict

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _provider_name(self) -> str:
        # Keep the API response honest about which provider actually answered.
        base_url = self.settings.openai_base_url.lower()
        if "groq" in base_url:
            return "groq"
        if "meta.ai" in base_url:
            return "meta"
        if "googleapis" in base_url or "generativelanguage" in base_url:
            return "gemini"
        return "openai"

    async def analyze_comment(self, *, name: str, email: str, comment: str) -> Dict[str, Any]:
        if not self.settings.openai_api_key:
            raise RuntimeError("openai api key is not configured")

        prompt = (
            "You are a backend assistant analyzing a contact form message. "
            "Return strict JSON with keys: category, sentiment, priority, summary, suggested_reply. "
            "Categories: job_offer, project_request, support, general. "
            "Sentiment: positive, neutral, negative. "
            "Priority: low, medium, high. "
            f"Name: {name}\nEmail: {email}\nComment: {comment}"
        )

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": "Return only JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self.settings.ai_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.openai_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        try:
            import json

            parsed = json.loads(content)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("OpenAI response parsing failed: %s", exc)
            raise RuntimeError("openai response parsing failed") from exc

        return {
            "provider": self._provider_name(),
            "status": "success",
            "fallback_reason": None,
            **parsed,
        }
