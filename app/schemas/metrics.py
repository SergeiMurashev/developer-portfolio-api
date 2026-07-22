from typing import Dict

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_contacts: int
    ai_success: int
    ai_fallback: int
    email_failures: int
    categories: Dict[str, int]

