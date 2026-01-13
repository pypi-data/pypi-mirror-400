"""Generate llms.txt markdown from OpenAPI schema."""

from typing import Any


def generate_llms_txt(openapi_schema: dict[str, Any]) -> str:
    """Convert an OpenAPI schema to llms.txt markdown format.

    Args:
        openapi_schema: OpenAPI 3.x schema dictionary

    Returns:
        Markdown string in llms.txt format
    """
    lines: list[str] = []

    # H1: API Title
    info = openapi_schema.get("info", {})
    title = info.get("title", "API")
    lines.append(f"# {title}")
    lines.append("")

    # Blockquote: Description
    description = info.get("description")
    if description:
        # Handle multi-line descriptions
        for line in description.strip().split("\n"):
            lines.append(f"> {line}")
        lines.append("")

    # Schema definitions section (at the top, before endpoints)
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    _format_schema_definitions(lines, schemas)

    # Group endpoints by tag
    paths = openapi_schema.get("paths", {})
    endpoints_by_tag: dict[str, list[dict[str, Any]]] = {}

    for path, path_item in paths.items():
        for method in ["get", "post", "put", "patch", "delete", "head", "options"]:
            if method not in path_item:
                continue

            operation = path_item[method]
            tags = operation.get("tags", ["Endpoints"])
            tag = tags[0] if tags else "Endpoints"

            if tag not in endpoints_by_tag:
                endpoints_by_tag[tag] = []

            endpoints_by_tag[tag].append({
                "path": path,
                "method": method.upper(),
                "operation": operation,
                "schemas": openapi_schema.get("components", {}).get("schemas", {}),
            })

    # Generate sections by tag
    for tag, endpoints in endpoints_by_tag.items():
        lines.append(f"## {tag}")
        lines.append("")

        for endpoint in endpoints:
            _format_endpoint(lines, endpoint)

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _format_endpoint(lines: list[str], endpoint: dict[str, Any]) -> None:
    """Format a single endpoint."""
    method = endpoint["method"]
    path = endpoint["path"]
    operation = endpoint["operation"]
    schemas = endpoint["schemas"]

    summary = operation.get("summary", "")
    description = operation.get("description", "")

    # H3 endpoint heading with summary
    if summary:
        lines.append(f"### `{method} {path}` - {summary}")
    else:
        lines.append(f"### `{method} {path}`")
    lines.append("")

    # Show description if present (and different from summary)
    if description and description != summary:
        # Indent each line of description
        for desc_line in description.strip().split("\n"):
            lines.append(f"> {desc_line}" if desc_line.strip() else ">")
        lines.append("")

    # Parameters
    parameters = operation.get("parameters", [])
    if parameters:
        lines.append("- **Request Parameters**:")
        for param in parameters:
            _format_parameter(lines, param)

    # Request body
    request_body = operation.get("requestBody")
    if request_body:
        _format_request_body(lines, request_body, schemas)

    # Response
    responses = operation.get("responses", {})
    _format_responses(lines, responses, schemas)

    lines.append("")


def _format_parameter(lines: list[str], param: dict[str, Any]) -> None:
    """Format a parameter."""
    name = param.get("name", "")
    param_in = param.get("in", "query")
    required = param.get("required", False)
    description = param.get("description", "")

    schema = param.get("schema", {})
    param_type = _get_type_string(schema)

    required_str = "required" if required else "optional"
    location = f" ({param_in})" if param_in != "query" else ""

    if description:
        lines.append(f"  - `{name}` ({param_type}, {required_str}){location}: {description}")
    else:
        lines.append(f"  - `{name}` ({param_type}, {required_str}){location}")


def _format_request_body(
    lines: list[str], request_body: dict[str, Any], schemas: dict[str, Any]
) -> None:
    """Format request body."""
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})

    if not schema:
        return

    # Resolve $ref if present
    schema = _resolve_ref(schema, schemas)

    required_fields = set(schema.get("required", []))
    properties = schema.get("properties", {})

    if properties:
        lines.append("- **Body**:")
        for prop_name, prop_schema in properties.items():
            prop_schema = _resolve_ref(prop_schema, schemas)
            prop_type = _get_type_string(prop_schema)
            prop_desc = prop_schema.get("description", "")
            required_str = "required" if prop_name in required_fields else "optional"

            if prop_desc:
                lines.append(f"  - `{prop_name}` ({prop_type}, {required_str}): {prop_desc}")
            else:
                lines.append(f"  - `{prop_name}` ({prop_type}, {required_str})")


def _format_responses(
    lines: list[str], responses: dict[str, Any], schemas: dict[str, Any]
) -> None:
    """Format response information."""
    # Focus on success responses (2xx)
    for status_code in ["200", "201", "204"]:
        if status_code not in responses:
            continue

        response = responses[status_code]
        _format_single_response(lines, status_code, response, schemas)
        return

    # Fallback: use first response
    if responses:
        first_code = next(iter(responses))
        response = responses[first_code]
        _format_single_response(lines, first_code, response, schemas)


def _format_single_response(
    lines: list[str],
    status_code: str,
    response: dict[str, Any],
    schemas: dict[str, Any],
) -> None:
    """Format a single response with type information."""
    description = response.get("description", "")

    # Extract response type from content schema
    response_type = _get_response_type(response, schemas)

    if response_type and description:
        lines.append(f"- **Returns** ({status_code}): {response_type} - {description}")
    elif response_type:
        lines.append(f"- **Returns** ({status_code}): {response_type}")
    elif description:
        lines.append(f"- **Returns** ({status_code}): {description}")

    # Format response properties
    _format_response_properties(lines, response, schemas)


def _format_response_properties(
    lines: list[str], response: dict[str, Any], schemas: dict[str, Any]
) -> None:
    """Format response schema properties (two levels deep)."""
    content = response.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})

    if not schema:
        return

    # Resolve $ref if present
    schema = _resolve_ref(schema, schemas)

    # Handle array types - show properties of the item type
    if schema.get("type") == "array":
        items = schema.get("items", {})
        schema = _resolve_ref(items, schemas)

    properties = schema.get("properties", {})
    if not properties:
        return

    for prop_name, prop_schema_orig in properties.items():
        prop_schema = _resolve_ref(prop_schema_orig, schemas)
        prop_type = _get_type_string(prop_schema_orig)
        prop_desc = prop_schema.get("description", "")

        if prop_desc:
            lines.append(f"  - `{prop_name}` ({prop_type}): {prop_desc}")
        else:
            lines.append(f"  - `{prop_name}` ({prop_type})")


def _get_response_type(response: dict[str, Any], schemas: dict[str, Any]) -> str | None:
    """Extract type string from response schema."""
    content = response.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})

    if not schema:
        return None

    return _get_type_string(schema)


def _resolve_ref(schema: dict[str, Any], schemas: dict[str, Any]) -> dict[str, Any]:
    """Resolve a $ref to its schema definition."""
    ref = schema.get("$ref")
    if not ref:
        return schema

    # Handle #/components/schemas/Name format
    if ref.startswith("#/components/schemas/"):
        schema_name = ref.split("/")[-1]
        return schemas.get(schema_name, schema)

    return schema


def _get_type_string(schema: dict[str, Any]) -> str:
    """Get a human-readable type string from a schema."""
    schema_type = schema.get("type", "object")

    if schema_type == "array":
        items = schema.get("items", {})
        items_type = _get_type_string(items)
        return f"array[{items_type}]"

    if "enum" in schema:
        enum_values = schema["enum"]
        return f"enum[{', '.join(str(v) for v in enum_values)}]"

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/components/schemas/"):
            return f"${ref.split('/')[-1]}"
        return "object"

    return schema_type


def _format_schema_definitions(lines: list[str], schemas: dict[str, Any]) -> None:
    """Format schema definitions section at the top of the document."""
    if not schemas:
        return

    lines.append("## Schema Definitions")
    lines.append("")
    lines.append("> Reusable schema types referenced throughout the API.")
    lines.append("")

    for schema_name, schema in schemas.items():
        lines.append(f"### ${schema_name}")
        lines.append("")

        description = schema.get("description")
        if description:
            for line in description.strip().split("\n"):
                lines.append(f"> {line}" if line.strip() else ">")
            lines.append("")

        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))

        if properties:
            lines.append("Properties:")
            for prop_name, prop_schema in properties.items():
                prop_type = _get_type_string(prop_schema)
                prop_desc = prop_schema.get("description", "")
                required_str = " (required)" if prop_name in required_fields else ""

                if prop_desc:
                    lines.append(f"- `{prop_name}` ({prop_type}{required_str}): {prop_desc}")
                else:
                    lines.append(f"- `{prop_name}` ({prop_type}{required_str})")
            lines.append("")
        else:
            # Handle schemas without properties (e.g., enums, primitives)
            schema_type = schema.get("type")
            if "enum" in schema:
                enum_values = schema["enum"]
                lines.append(f"Type: enum[{', '.join(str(v) for v in enum_values)}]")
                lines.append("")
            elif schema_type:
                lines.append(f"Type: {schema_type}")
                lines.append("")
