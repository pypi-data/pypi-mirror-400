"""Tests for the router module."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fast_llms_txt import create_llms_txt_router


class TestCreateLlmsTxtRouter:
    """Tests for create_llms_txt_router function."""

    def test_default_path(self):
        """Test that default path is /llms.txt."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert response.status_code == 200

    def test_custom_path(self):
        """Test custom endpoint path."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app, path="/docs.txt"))

        client = TestClient(app)
        response = client.get("/docs.txt")

        assert response.status_code == 200

    def test_with_prefix(self):
        """Test router with prefix."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app), prefix="/api/v1/docs")

        client = TestClient(app)
        response = client.get("/api/v1/docs/llms.txt")

        assert response.status_code == 200

    def test_content_type(self):
        """Test that response content type is text/plain."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "text/plain" in response.headers["content-type"]

    def test_returns_markdown(self):
        """Test that response contains markdown content."""
        app = FastAPI(title="Test API", description="A test API")

        @app.get("/users")
        def list_users():
            """List all users."""
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "# Test API" in response.text
        assert "> A test API" in response.text
        assert "GET /users" in response.text

    def test_endpoint_not_in_schema(self):
        """Test that llms.txt endpoint is not included in OpenAPI schema."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        schema = app.openapi()

        assert "/llms.txt" not in schema.get("paths", {})

    def test_reflects_app_changes(self):
        """Test that generated content reflects current app state."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)

        # Initially no endpoints
        response1 = client.get("/llms.txt")
        assert "/users" not in response1.text

        # Add an endpoint
        @app.get("/users")
        def list_users():
            return []

        # Clear cached schema
        app.openapi_schema = None

        response2 = client.get("/llms.txt")
        assert "/users" in response2.text

    def test_with_tags(self):
        """Test that tags are properly reflected."""
        app = FastAPI(title="Test API")

        @app.get("/users", tags=["Users"])
        def list_users():
            return []

        @app.get("/posts", tags=["Posts"])
        def list_posts():
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "## Users" in response.text
        assert "## Posts" in response.text

    def test_with_parameters(self):
        """Test that parameters are included."""
        app = FastAPI(title="Test API")

        @app.get("/users")
        def list_users(limit: int = 10, offset: int = 0):
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "limit" in response.text
        assert "offset" in response.text

