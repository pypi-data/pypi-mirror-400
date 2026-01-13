from typing import List, Optional

from pydantic import BaseModel, Field


class LocatedData(BaseModel):
    """Model representing the coordinates found for a specific value in a document."""

    target_coordinates: Optional[List[float]] = Field(
        None, description="The [x, y, w, h] coordinates normalized to 0-1."
    )
