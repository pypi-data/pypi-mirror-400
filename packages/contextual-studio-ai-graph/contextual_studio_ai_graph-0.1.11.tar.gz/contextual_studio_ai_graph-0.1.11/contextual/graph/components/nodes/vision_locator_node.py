import base64
import logging
from typing import Any, Dict, Optional

import fitz  # PyMuPDF
from langchain_core.messages import HumanMessage
from pydantic import Field

from contextual.graph.models import Coordinates, LocatedData, State

from .base import BaseNode

logger = logging.getLogger(__name__)


class VisionLocatorNode(BaseNode):
    """Node that locates a specific text value on a specific page using Vision LLM."""

    llm_service: Any = Field(..., description="The language model service client (Vision capable).")

    async def process(
        self, state: State, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Locates the target value coordinates on the specified page."""

        if not state.file_path or not state.target_value or not state.target_page:
            return {"target_coordinates": None}

        tracer = getattr(self, "_tracer", None)

        try:
            # 1. Log INIT
            if tracer and state.execution_id:
                await tracer.log_step(
                    state.execution_id,
                    "VISION_SEARCH_INIT",
                    "SUCCESS",
                    metadata={
                        "target_value": state.target_value,
                        "target_page": state.target_page,
                        "expected_schema": Coordinates.model_json_schema(),
                    },
                )

            # 2. Convert PDF Page to Image (PyMuPDF)
            doc = fitz.open(state.file_path)
            if state.target_page - 1 >= len(doc):
                return {"target_coordinates": None}

            page = doc.load_page(state.target_page - 1)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")

            # Encode image to base64
            image_b64 = base64.b64encode(img_data).decode("utf-8")
            image_url = f"data:image/png;base64,{image_b64}"

            doc.close()

            # 3. Invoke LLM with Vision
            structured_llm = self.llm_service.with_structured_output(Coordinates)

            prompt = (
                f"Find the bounding box for the text: '{state.target_value}'. "
                f"Return the coordinates [ymin, xmin, ymax, xmax] normalized to 0-1000 scale."
            )

            # Construct message compatible with LangChain Google adapter using HumanMessage
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": image_url},
                ]
            )

            # We assume llm_service is a ChatGoogleGenerativeAI instance or compatible wrapper
            result: Coordinates = await structured_llm.ainvoke([message])

            found = False
            coordinates = None
            raw_box = None

            # 4. Convert [ymin, xmin, ymax, xmax] (0-1000) to [x, y, w, h] (0-1)
            if result and result.box_2d:
                ymin, xmin, ymax, xmax = result.box_2d
                raw_box = result.box_2d

                # Normalize 0-1000 to 0-1
                n_ymin = ymin / 1000.0
                n_xmin = xmin / 1000.0
                n_ymax = ymax / 1000.0
                n_xmax = xmax / 1000.0

                # Convert to [x, y, w, h] format expected by frontend
                x = n_xmin
                y = n_ymin
                w = n_xmax - n_xmin
                h = n_ymax - n_ymin

                coordinates = [x, y, w, h]
                found = True

            # 5. Log RESULT
            if tracer and state.execution_id:
                await tracer.log_step(
                    state.execution_id,
                    "VISION_SEARCH_RESULT",
                    "SUCCESS",
                    metadata={
                        "found": found,
                        "coordinates_normalized": coordinates,
                        "raw_box_2d": raw_box,
                        "model_output_dump": result.model_dump() if result else None,
                    },
                )

            if found:
                return {"target_coordinates": LocatedData(target_coordinates=coordinates)}

            return {"target_coordinates": LocatedData(target_coordinates=None)}

        except Exception as e:
            logger.error(f"Locator Error: {e}", exc_info=True)
            return {"target_coordinates": LocatedData(target_coordinates=None)}
