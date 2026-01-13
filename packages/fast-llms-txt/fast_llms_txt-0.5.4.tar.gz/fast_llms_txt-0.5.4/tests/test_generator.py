"""Tests for the generator module."""

from fast_llms_txt.generator import generate_llms_txt


class TestGenerateLlmsTxt:
    """Tests for generate_llms_txt function."""

    def test_basic_api_info(self):
        """Test that API title and description are included."""
        schema = {
            "info": {
                "title": "My API",
                "description": "A sample API",
            },
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# My API" in result
        assert "> A sample API" in result

    def test_multiline_description(self):
        """Test that multiline descriptions are properly formatted."""
        schema = {
            "info": {
                "title": "My API",
                "description": "Line one\nLine two",
            },
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "> Line one" in result
        assert "> Line two" in result

    def test_missing_description(self):
        """Test handling of missing description."""
        schema = {
            "info": {"title": "My API"},
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# My API" in result
        assert ">" not in result

    def test_endpoint_with_summary(self):
        """Test endpoint formatting with summary."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "### `GET /users` - List users" in result

    def test_endpoint_with_description_fallback(self):
        """Test that description is shown in blockquote when no summary."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "description": "Retrieve all users",
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "### `GET /users`" in result
        assert "> Retrieve all users" in result

    def test_endpoint_grouped_by_tag(self):
        """Test that endpoints are grouped by tag."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "tags": ["Users"],
                        "summary": "List users",
                        "responses": {},
                    }
                },
                "/posts": {
                    "get": {
                        "tags": ["Posts"],
                        "summary": "List posts",
                        "responses": {},
                    }
                },
            },
        }

        result = generate_llms_txt(schema)

        assert "## Users" in result
        assert "## Posts" in result

    def test_default_endpoints_tag(self):
        """Test that endpoints without tags use 'Endpoints' heading."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "## Endpoints" in result

    def test_query_parameter(self):
        """Test query parameter formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"},
                                "description": "Max results",
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`limit` (integer, optional): Max results" in result

    def test_required_parameter(self):
        """Test required parameter formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`id` (string, required) (path)" in result

    def test_request_body(self):
        """Test request body formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "User name",
                                            },
                                            "email": {
                                                "type": "string",
                                                "description": "User email",
                                            },
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Body**:" in result
        assert "`name` (string, required): User name" in result
        assert "`email` (string, optional): User email" in result

    def test_response_description(self):
        """Test response description formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {"description": "List of users"},
                            "404": {"description": "Not found"},
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (200): List of users" in result

    def test_201_response_priority(self):
        """Test that 201 response is used for POST endpoints."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "responses": {
                            "201": {"description": "User created"},
                            "400": {"description": "Bad request"},
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (201): User created" in result

    def test_array_type(self):
        """Test array type formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "ids",
                                "in": "query",
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "array[string]" in result

    def test_enum_type(self):
        """Test enum type formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "status",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "enum": ["active", "inactive"],
                                },
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "enum[active, inactive]" in result

    def test_schema_ref(self):
        """Test $ref in request body shows type reference, not expanded properties."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "responses": {},
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "description": "User name"}
                        },
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        # Request body shows type reference, not expanded properties
        assert "**Body**: $User" in result
        # Properties are in Schema Definitions section
        assert "### $User" in result
        assert "`name` (string (required)): User name" in result

    def test_multiple_http_methods(self):
        """Test that multiple HTTP methods on same path are handled."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {"summary": "List users", "responses": {}},
                    "post": {"summary": "Create user", "responses": {}},
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`GET /users`" in result
        assert "`POST /users`" in result

    def test_empty_paths(self):
        """Test handling of empty paths."""
        schema = {
            "info": {"title": "API"},
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# API" in result
        assert "##" not in result

    def test_response_type_from_schema(self):
        """Test that response type is extracted from schema with $ prefix."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"},
                                        }
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {"schemas": {"User": {"type": "object"}}},
        }

        result = generate_llms_txt(schema)

        assert "array[$User]" in result

    def test_response_type_with_ref(self):
        """Test response type with $ref uses $ prefix."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {"schemas": {"User": {"type": "object"}}},
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (200): $User - Success" in result

    def test_response_properties_with_ref(self):
        """Test that response properties are expanded for $ref schemas."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "User ID"},
                            "name": {"type": "string"},
                            "email": {"type": "string", "description": "User email"},
                        },
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`id` (string): User ID" in result
        assert "`name` (string)" in result
        assert "`email` (string): User email" in result

    def test_response_properties_inline_schema(self):
        """Test that response properties are expanded for inline schemas."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/status": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "uptime": {"type": "integer", "description": "Seconds running"},
                                            },
                                        }
                                    }
                                },
                            }
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`status` (string)" in result
        assert "`uptime` (integer): Seconds running" in result

    def test_response_properties_array_type(self):
        """Test that array response types use $ prefix for refs."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "List of users",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"},
                                        }
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                        },
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        # Response type uses $ prefix
        assert "array[$User]" in result
        # Schema definitions section shows properties
        assert "### $User" in result
        assert "`id` (string)" in result
        assert "`name` (string)" in result

    def test_response_no_properties(self):
        """Test graceful handling of responses without properties."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/ping": {
                    "get": {
                        "responses": {
                            "204": {"description": "No content"}
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (204): No content" in result

    def test_nested_ref_property_expansion(self):
        """Test that $ref properties use $ prefix and schemas are in definitions."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/response": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Response"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Response": {
                        "type": "object",
                        "properties": {
                            "data": {"$ref": "#/components/schemas/DataItem"},
                            "meta": {"$ref": "#/components/schemas/Meta"},
                        },
                    },
                    "DataItem": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string", "description": "Item name"},
                        },
                    },
                    "Meta": {
                        "type": "object",
                        "properties": {
                            "total": {"type": "integer"},
                        },
                    },
                }
            },
        }

        result = generate_llms_txt(schema)

        # Response properties reference other schemas with $ prefix
        assert "`data` ($DataItem)" in result
        assert "`meta` ($Meta)" in result

        # Schema definitions section contains all schemas
        assert "## Schema Definitions" in result
        assert "### $Response" in result
        assert "### $DataItem" in result
        assert "### $Meta" in result

        # DataItem properties are in the schema definitions
        assert "`name` (string): Item name" in result
        assert "`total` (integer)" in result

    def test_nested_array_ref_property_expansion(self):
        """Test that array properties with $ref items use $ prefix."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/items": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/ListResponse"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "ListResponse": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Item"},
                            },
                        },
                    },
                    "Item": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "value": {"type": "number"},
                        },
                    },
                }
            },
        }

        result = generate_llms_txt(schema)

        # Array type uses $ prefix for items
        assert "`items` (array[$Item])" in result

        # Schema definitions section has both schemas
        assert "### $ListResponse" in result
        assert "### $Item" in result

        # Item properties are in schema definitions
        assert "`id` (string)" in result
        assert "`value` (number)" in result
