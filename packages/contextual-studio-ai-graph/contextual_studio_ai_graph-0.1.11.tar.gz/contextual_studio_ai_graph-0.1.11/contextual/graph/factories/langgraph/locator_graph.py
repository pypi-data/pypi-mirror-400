from typing import Any, Optional

from langgraph.graph import StateGraph

from contextual.graph.components.observability import MongoExecutionTracer, TraceNodeMiddleware

from ...components.nodes import VisionLocatorNode
from ...components.repositories.mongodb_crud_repository import MongoDBRepository
from ...models import DataExtractorConfig
from ..llm_services import GoogleLLMFactory
from .base import GraphFactory


class LocatorLangGraphFactory(GraphFactory):
    """Factory for constructing locator graphs."""

    def __init__(
        self,
        config: Optional[DataExtractorConfig] = None,
        execution_tracing_repository: Optional[MongoDBRepository] = None,
    ):
        self.config = config
        self.execution_tracing_repository = execution_tracing_repository

    def build(self, state: type[Any]) -> Any:
        """Build and compile the locator graph."""
        graph = StateGraph(state)

        # Instantiate Tracer
        tracer: Optional[MongoExecutionTracer] = None
        if self.execution_tracing_repository:
            tracer = MongoExecutionTracer(repository=self.execution_tracing_repository)

        node_name = "vision_locator"

        # Configure LLM (use config or default)
        llm_kwargs = {}
        if self.config:
            if self.config.api_key:
                llm_kwargs["api_key"] = self.config.api_key.get_secret_value()
            if self.config.llm:
                llm_kwargs["model"] = self.config.llm.model_name

        llm_service = GoogleLLMFactory.create(**llm_kwargs)

        locator_node = VisionLocatorNode(llm_service=llm_service)

        if tracer:
            traced_node = TraceNodeMiddleware(
                inner_node=locator_node, tracer=tracer, step_name="LOCATE_COORDINATES"
            )
            graph.add_node(node_name, traced_node.as_langgraph_node())
        else:
            graph.add_node(node_name, locator_node.as_langgraph_node())

        graph.set_entry_point(node_name)
        graph.set_finish_point(node_name)

        return graph.compile()
