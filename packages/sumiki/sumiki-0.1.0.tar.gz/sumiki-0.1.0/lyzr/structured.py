"""
Utilities for structured response handling with Pydantic models
"""

from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, ValidationError as PydanticValidationError


class ResponseSchemaBuilder:
    """
    Build OpenAI json_schema format from Pydantic models

    Converts Pydantic BaseModel classes into the json_schema format
    required by the Lyzr Agent API for structured responses.
    """

    @staticmethod
    def to_json_schema(
        model: Type[BaseModel],
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert Pydantic model to OpenAI json_schema format

        Args:
            model: Pydantic BaseModel class
            name: Optional schema name (defaults to model class name)

        Returns:
            Dict in OpenAI json_schema format:
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "SchemaName",
                    "strict": True,
                    "schema": {...}
                }
            }

        Example:
            >>> from pydantic import BaseModel
            >>> from typing import Literal
            >>>
            >>> class TestResult(BaseModel):
            ...     result: Literal["Pass", "Fail"]
            ...     reason: str
            >>>
            >>> schema = ResponseSchemaBuilder.to_json_schema(TestResult)
            >>> print(schema["json_schema"]["name"])
            TestResult
        """
        # Get JSON schema from Pydantic (v2 API)
        pydantic_schema = model.model_json_schema()

        # Extract key components
        properties = pydantic_schema.get("properties", {})
        required = pydantic_schema.get("required", [])
        description = pydantic_schema.get("description")

        # Build OpenAI json_schema format
        schema_name = name or model.__name__

        # Clean up nested schemas (handle $defs references)
        defs = pydantic_schema.get("$defs", {})
        cleaned_properties = ResponseSchemaBuilder._resolve_refs(properties, defs)

        openai_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": cleaned_properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        }

        # Add description if present
        if description:
            openai_schema["json_schema"]["schema"]["description"] = description

        return openai_schema

    @staticmethod
    def _resolve_refs(
        properties: Dict[str, Any],
        defs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve $ref references in properties and ensure additionalProperties: false

        Pydantic uses $ref for nested models. OpenAI json_schema requires:
        1. Inline definitions (no $ref)
        2. additionalProperties: false on ALL objects

        Args:
            properties: Property definitions (may contain $ref)
            defs: Schema definitions ($defs section)

        Returns:
            Properties with resolved references and additionalProperties set
        """
        resolved = {}

        for prop_name, prop_schema in properties.items():
            if "$ref" in prop_schema:
                # Extract reference name
                ref_path = prop_schema["$ref"]
                ref_name = ref_path.split("/")[-1]

                # Look up in $defs
                if ref_name in defs:
                    # Inline the definition
                    inline_def = defs[ref_name].copy()
                    # Ensure additionalProperties: false for objects
                    if inline_def.get("type") == "object":
                        inline_def["additionalProperties"] = False
                        # Ensure required field exists
                        if "required" not in inline_def:
                            inline_def["required"] = list(inline_def.get("properties", {}).keys())
                    # Recursively resolve nested refs
                    if "properties" in inline_def:
                        inline_def["properties"] = ResponseSchemaBuilder._resolve_refs(
                            inline_def["properties"], defs
                        )
                    resolved[prop_name] = inline_def
                else:
                    resolved[prop_name] = prop_schema
            elif "items" in prop_schema and isinstance(prop_schema["items"], dict):
                # Handle array items with $ref
                if "$ref" in prop_schema["items"]:
                    ref_path = prop_schema["items"]["$ref"]
                    ref_name = ref_path.split("/")[-1]

                    if ref_name in defs:
                        resolved_schema = prop_schema.copy()
                        inline_def = defs[ref_name].copy()
                        # Ensure additionalProperties: false for objects
                        if inline_def.get("type") == "object":
                            inline_def["additionalProperties"] = False
                            # Ensure required field exists
                            if "required" not in inline_def:
                                inline_def["required"] = list(inline_def.get("properties", {}).keys())
                        # Recursively resolve nested refs
                        if "properties" in inline_def:
                            inline_def["properties"] = ResponseSchemaBuilder._resolve_refs(
                                inline_def["properties"], defs
                            )
                        resolved_schema["items"] = inline_def
                        resolved[prop_name] = resolved_schema
                    else:
                        resolved[prop_name] = prop_schema
                else:
                    # Regular array items - ensure additionalProperties if object
                    resolved_schema = prop_schema.copy()
                    if isinstance(prop_schema["items"], dict) and prop_schema["items"].get("type") == "object":
                        items_copy = prop_schema["items"].copy()
                        items_copy["additionalProperties"] = False
                        resolved_schema["items"] = items_copy
                    resolved[prop_name] = resolved_schema
            elif "anyOf" in prop_schema:
                # Handle Optional fields (anyOf: [type, null])
                # Simplify by taking the non-null type
                non_null_types = [
                    t for t in prop_schema["anyOf"]
                    if t.get("type") != "null"
                ]
                if non_null_types:
                    non_null = non_null_types[0].copy()
                    # Ensure additionalProperties if object
                    if non_null.get("type") == "object":
                        non_null["additionalProperties"] = False
                    resolved[prop_name] = non_null
                else:
                    resolved[prop_name] = prop_schema
            else:
                # Regular property - ensure additionalProperties if object
                if prop_schema.get("type") == "object":
                    resolved_schema = prop_schema.copy()
                    resolved_schema["additionalProperties"] = False
                    resolved[prop_name] = resolved_schema
                else:
                    resolved[prop_name] = prop_schema

        return resolved


class ResponseParser:
    """
    Parse and validate structured responses against Pydantic models

    Uses json_repair to handle malformed JSON, then validates against
    the provided Pydantic model.
    """

    @staticmethod
    def parse(
        response_str: str,
        model: Type[BaseModel]
    ) -> BaseModel:
        """
        Parse JSON string and validate against Pydantic model

        Args:
            response_str: JSON string response from agent
            model: Pydantic BaseModel class to validate against

        Returns:
            Validated Pydantic model instance

        Raises:
            InvalidResponseError: If JSON parsing or validation fails

        Example:
            >>> from pydantic import BaseModel
            >>> from typing import Literal
            >>>
            >>> class Result(BaseModel):
            ...     status: Literal["success", "failure"]
            >>>
            >>> json_str = '{"status": "success"}'
            >>> result = ResponseParser.parse(json_str, Result)
            >>> print(result.status)
            success
        """
        try:
            import json_repair
        except ImportError:
            raise ImportError(
                "json-repair is required for structured responses. "
                "Install it with: pip install json-repair"
            )

        from lyzr.exceptions import InvalidResponseError

        try:
            # Parse JSON using json_repair (handles malformed JSON)
            data = json_repair.loads(response_str)

            # Ensure data is a dict (json_repair might return string in some cases)
            if isinstance(data, str):
                # Try standard json as fallback
                import json
                data = json.loads(data)

            if not isinstance(data, dict):
                raise InvalidResponseError(
                    f"Expected JSON object, got {type(data).__name__}",
                    response=response_str,
                    validation_error=None
                )

            # Validate with Pydantic
            instance = model(**data)
            return instance

        except PydanticValidationError as validation_error:
            # Handle Pydantic validation errors
            error_details = validation_error.errors()
            print(f"\n⚠️  Pydantic Validation Error:")
            print(f"Raw response from agent:\n{response_str}\n")
            print(f"Validation errors: {error_details}")
            raise InvalidResponseError(
                f"Response validation failed: {len(error_details)} error(s)",
                response=response_str,
                validation_error=validation_error
            )
        except InvalidResponseError:
            # Re-raise our custom errors
            raise
        except Exception as json_error:
            # Handle other JSON parsing errors
            print(f"\n⚠️  JSON Parsing Error:")
            print(f"Raw response from agent:\n{response_str}\n")
            print(f"Error: {str(json_error)}")
            raise InvalidResponseError(
                f"Failed to parse JSON response: {str(json_error)}",
                response=response_str,
                validation_error=None
            )
