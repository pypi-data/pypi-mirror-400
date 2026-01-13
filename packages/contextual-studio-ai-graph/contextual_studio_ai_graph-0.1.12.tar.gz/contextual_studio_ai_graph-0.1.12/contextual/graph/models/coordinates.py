from typing import List, Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Model representing normalized coordinates [ymin, xmin, ymax, xmax] (0-1000) from LLM."""

    box_2d: Optional[List[int]] = Field(
        None,
        description="The bounding box [ymin, xmin, ymax, xmax] of the value in the image. Use integers from 0 to 1000.",
    )
