from typing import Any, Dict, Optional

from pydantic import Field

from ...models import State
from ..nodes.base import BaseNode
from .tracer_interface import BaseExecutionTracer


class TraceNodeMiddleware(BaseNode):
    """Middleware wrapper to add execution tracing to graph nodes."""

    inner_node: BaseNode = Field(..., description="The node to be wrapped.")
    tracer: BaseExecutionTracer = Field(..., description="The tracer service.")
    step_name: str = Field(..., description="The name of the step for tracing.")

    async def process(
        self, state: State, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Wraps the inner node process with logging calls."""

        execution_id = state.execution_id

        if not execution_id:
            return await self.inner_node.process(state, config)

        try:
            # Determine suffix for repeating steps if needed.
            # We count how many times this step has started.
            # Example: If there are 0 "LOCATE_COORDINATES", this is "LOCATE_COORDINATES_1" (if we want 1-based)
            # Or just append the suffix if count > 0 to keep backward compatibility?
            # User specifically asked for _1, _2... so let's enforce it for LOCATE_COORDINATES at least, or always.

            # Let's count existing steps that START with this name
            tracer_idx = 1
            prev_count = await self.tracer.get_step_count(execution_id, self.step_name)
            tracer_idx = prev_count + 1

            # We will use the indexed name only if prev_count > 0 OR specific steps requested by user logic?
            # The user request implies they want ALL of them numbered effectively if there are multiple.
            # To be safe and cleaner, if it's the first one, maybe no suffix? Or suffix _1 always?
            # User showed "VISION_SEARCH_INIT_1" and "VISION_SEARCH_RESULT_1" in their manual implementation.
            # And asked "Los locate coordinates también deberían tener el _1, _2...".
            # So I will apply it: if it's LOCATE_COORDINATES, always append _N.

            current_step_name = self.step_name
            if self.step_name == "LOCATE_COORDINATES":
                current_step_name = f"{self.step_name}_{tracer_idx}"

            # Note: For other steps we might want to keep behavior or apply it universally.
            # Let's apply it only for LOCATE_COORDINATES for now to avoid breaking other logic unforeseen,
            # unless we prefer consistency.
            # Given the context is specifically about the locator loop, being specific is safer.

            await self.tracer.log_step(execution_id, current_step_name, "IN_PROGRESS")

            # Inject the tracer into the inner node so it can log granular updates
            # This is critical for ZeroxOCRNode to access the tracer via self._tracer
            object.__setattr__(self.inner_node, "_tracer", self.tracer)

            result = await self.inner_node.process(state, config)

            await self.tracer.log_step(execution_id, current_step_name, "SUCCESS")

            return result
        except Exception as e:
            # Use the same name we started with
            # But wait, if we crash before assigning current_step_name? It's inside try, but assignment is first thing.
            # Actually, `current_step_name` might be unbound if crash happens strictly at `get_step_count`.
            # But `get_step_count` is what we added.
            # Let's initialize `current_step_name` before try or handle it.
            # Better: put logic inside try.

            log_name = locals().get("current_step_name", self.step_name)
            await self.tracer.log_step(execution_id, log_name, "FAILED", str(e))
            raise e
