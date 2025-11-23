"""Intent output schema for ADK structured output."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class IntentOutputSchema(BaseModel):
    """Schema for intent recognition output from ADK."""

    intent: str = Field(..., description="Recognized intent (e.g., 'send_money')")
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities (amount, beneficiary, country, delivery_method)",
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)"
    )

    def get_entity(self, key: str, default: Any = None) -> Any:
        """Get entity value by key."""
        return self.entities.get(key, default)

    def has_entity(self, key: str) -> bool:
        """Check if entity exists."""
        return key in self.entities

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"IntentOutputSchema(intent='{self.intent}', "
            f"entities={self.entities}, confidence={self.confidence})"
        )

