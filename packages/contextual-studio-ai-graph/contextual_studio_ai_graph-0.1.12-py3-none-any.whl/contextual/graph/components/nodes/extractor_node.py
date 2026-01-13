import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from contextual.graph.components.extractor_schema import SchemaExtractor

from ...models import FilterSchema, ModelSchemaExtractor, State
from .base import BaseNode

logger = logging.getLogger(__name__)


class ExtractorNode(BaseNode):
    """Extracts structured data from text using a extractor_schema and an LLM.

    This node orchestrates a two-step process:
    1. Fetches and parses a specific extractor_schema definition via its extractor.
    2. Uses the parsed extractor_schema to instruct an LLM service to extract data
       from the input text.

    Attributes:
        llm_service: The language model service client for extraction.
        schema_extractor: The component responsible for retrieving the extractor_schema.
    """

    llm_service: Any = Field(..., description="The language model service client.")

    schema_extractor: SchemaExtractor = Field(
        ..., description="The service component to fetch extractor_schema definitions."
    )

    async def _get_parsed_schema(
        self, model_schema: Optional[BaseModel | Type[BaseModel] | FilterSchema]
    ) -> Type[BaseModel]:
        """Fetches the extractor_schema and parses it into a usable Pydantic model.

        Returns:
            The dynamically generated Pydantic model class.

        Raises:
            MongoDBCollectionNotFoundException: If the extractor_schema ID is not found.
            ValidationError: If the retrieved extractor_schema data is not valid.
            AttributeError: If the extractor_schema object is invalid.
        """
        schema_descriptor: ModelSchemaExtractor = await self.schema_extractor.extract(
            filters=model_schema
        )

        pydantic_class = schema_descriptor.as_pydantic_model()
        return pydantic_class

    async def _extract_data_with_llm(
        self,
        pydantic_class: Type[BaseModel],
        text_input: str | None,
        pages_input: Dict[int, str] | None,
        dataextractor_custom_prompt: str | None,
        config: Optional[Dict[str, Any]] = None,
        tracer: Any = None,
        execution_id: Optional[str] = None,
    ) -> Any:
        """Invokes the LLM service with the parsed extractor_schema to extract data."""
        try:
            # Extract schema information for the prompt
            schema_info = pydantic_class.model_json_schema()

            # Log INIT
            if tracer and execution_id:
                await tracer.log_step(
                    execution_id,
                    "DATA_EXTRACTION_INIT",
                    "SUCCESS",
                    metadata={"expected_schema": schema_info},
                )

            properties = schema_info.get("properties", {})

            schema_description_str = ""
            for field_name, field_info in properties.items():
                # We confirm we INCLUDE page fields now for explicit context
                description = field_info.get("description", "Sin descripción")
                # Add a visual indicator if it's a metadata field
                prefix = "  [META] " if field_name.endswith("_page") else "- "
                schema_description_str += f"{prefix}{field_name}: {description}\n"

            # Enhanced prompt with XML-style delimiters for robustness
            dataextractor_default_prompt = (
                "Eres un motor de extracción de datos de alta precisión.\n"
                "<instructions>\n"
                "1. Analiza el texto contenido EXCLUSIVAMENTE dentro de las etiquetas <document_context>.\n"
                "2. Extrae los datos definidos estrictamente en la sección <schema>.\n"
                "3. El texto contiene marcadores de paginación explícitos ('--- Página X ---').\n"
                "4. Para CADA valor extraído, debes identificar la página activa en ese punto del texto y rellenar su campo correspondiente '{nombre_campo}_page'.\n"
                "5. Responde ÚNICAMENTE con un objeto JSON válido. No incluyas bloques de código markdown, explicaciones ni texto fuera del JSON.\n"
                "</instructions>\n\n"
                "<schema>\n"
                f"{schema_description_str}"
                "</schema>\n\n"
                "Documento a procesar:\n"
            )

            # Format input: Use pages if available to give context, otherwise raw text
            final_input_text = ""
            if pages_input:
                for page_num, content in sorted(pages_input.items()):
                    final_input_text += f"\n--- Página {page_num} ---\n{content}\n"
            else:
                final_input_text = text_input or ""

            # Wrap the content in tags
            safe_text_input = f"<document_context>\n{final_input_text}\n</document_context>"

            # Construct final prompt (System Prompt + Document)
            if dataextractor_custom_prompt:
                # If custom prompt exists, we prepend it but keep the structure
                prompt = f"{dataextractor_custom_prompt}\n\n{dataextractor_default_prompt}\n{safe_text_input}"
            else:
                prompt = f"{dataextractor_default_prompt}\n{safe_text_input}"

            structured_llm = self.llm_service.with_structured_output(
                pydantic_class, include_raw=True
            )

            response = await structured_llm.ainvoke(prompt, config=config)
            extracted_data = response.get("parsed")
            # Serialize full response for deep tracing
            serialized_response = {}
            if isinstance(response, dict):
                for key, value in response.items():
                    try:
                        if hasattr(value, "model_dump"):
                            serialized_response[key] = value.model_dump()
                        elif hasattr(value, "dict"):
                            serialized_response[key] = value.dict()
                        else:
                            # Fallback, but try to keep structure if it's a dict
                            if isinstance(value, dict):
                                serialized_response[key] = value
                            else:
                                serialized_response[key] = str(value)
                    except Exception:
                        serialized_response[key] = str(value)
            else:
                serialized_response = {"raw_response": str(response)}

            # Log RESULT
            if tracer and execution_id:
                await tracer.log_step(
                    execution_id,
                    "DATA_EXTRACTION_RESULT",
                    "SUCCESS",
                    metadata={
                        "extracted_data_dump": (
                            extracted_data.model_dump() if extracted_data else None
                        ),
                        "full_response_dump": serialized_response,
                    },
                )

            return extracted_data
        except Exception as e:
            if tracer and execution_id:
                await tracer.log_step(
                    execution_id, "DATA_EXTRACTION_RESULT", "FAILED", metadata={"error": str(e)}
                )
            raise Exception(f"LLM service failed to extract data: {e}") from e

    async def process(
        self, state: State, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synchronously fetches a extractor_schema and extracts data from the state.

        Args:
            state: The input State object, expected to contain `text`.
            config: Optional runtime configuration passed by the graph.

        Returns:
            A dictionary containing the `data_extracted` field.
        """
        tracer = getattr(self, "_tracer", None)

        pydantic_class = await self._get_parsed_schema(state.model_schema)

        extracted_data = await self._extract_data_with_llm(
            pydantic_class,
            state.text,
            state.pages,
            state.dataextractor_custom_prompt,
            config,
            tracer,
            state.execution_id,
        )
        return {"data_extracted": extracted_data, "model_schema": pydantic_class}
