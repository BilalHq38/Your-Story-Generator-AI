"""Tests for story API endpoints."""

import pytest
from fastapi import status


class TestStoryEndpoints:
    """Tests for story CRUD operations."""

    def test_create_story(self, client, sample_story_data):
        """Test creating a new story."""
        response = client.post("/api/v1/stories/", json=sample_story_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["title"] == sample_story_data["title"]
        assert data["description"] == sample_story_data["description"]
        assert data["genre"] == sample_story_data["genre"]
        assert data["session_id"] is not None
        assert data["is_active"] is True

    def test_create_story_minimal(self, client):
        """Test creating a story with only required fields."""
        response = client.post(
            "/api/v1/stories/",
            json={"title": "Minimal Story"},
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == "Minimal Story"

    def test_create_story_validation_error(self, client):
        """Test validation error when title is missing."""
        response = client.post("/api/v1/stories/", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_stories(self, client, sample_story_data):
        """Test listing stories with pagination."""
        # Create a few stories
        for i in range(3):
            client.post(
                "/api/v1/stories/",
                json={**sample_story_data, "title": f"Story {i}"},
            )
        
        response = client.get("/api/v1/stories/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

    def test_list_stories_pagination(self, client, sample_story_data):
        """Test pagination parameters."""
        for i in range(5):
            client.post(
                "/api/v1/stories/",
                json={**sample_story_data, "title": f"Story {i}"},
            )
        
        response = client.get("/api/v1/stories/?page=2&page_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 2
        assert data["total_pages"] == 3

    def test_get_story(self, client, sample_story_data):
        """Test getting a specific story."""
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/stories/{story_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == story_id
        assert data["title"] == sample_story_data["title"]
        assert data["node_count"] == 0

    def test_get_story_not_found(self, client):
        """Test getting a non-existent story."""
        response = client.get("/api/v1/stories/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_story_by_session(self, client, sample_story_data):
        """Test getting a story by session ID."""
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        session_id = create_response.json()["session_id"]
        
        response = client.get(f"/api/v1/stories/session/{session_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["session_id"] == session_id

    def test_update_story(self, client, sample_story_data):
        """Test updating a story."""
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = create_response.json()["id"]
        
        response = client.patch(
            f"/api/v1/stories/{story_id}",
            json={"title": "Updated Title", "genre": "mystery"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == "Updated Title"
        assert data["genre"] == "mystery"
        assert data["description"] == sample_story_data["description"]

    def test_delete_story(self, client, sample_story_data):
        """Test deleting a story."""
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/stories/{story_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestStoryNodeEndpoints:
    """Tests for story node operations."""

    def test_create_node(self, client, sample_story_data, sample_node_data):
        """Test creating a story node."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json=sample_node_data,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["content"] == sample_node_data["content"]
        assert data["is_root"] is True  # First node becomes root
        assert data["depth"] == 0

    def test_create_child_node(self, client, sample_story_data, sample_node_data):
        """Test creating a child node."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        # Create root node
        root_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json=sample_node_data,
        )
        root_id = root_response.json()["id"]
        
        # Create child node
        child_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json={
                "content": "You enter the temple...",
                "choice_text": "Enter the temple",
                "parent_id": root_id,
            },
        )
        
        assert child_response.status_code == status.HTTP_201_CREATED
        data = child_response.json()
        
        assert data["parent_id"] == root_id
        assert data["is_root"] is False
        assert data["depth"] == 1

    def test_list_nodes(self, client, sample_story_data, sample_node_data):
        """Test listing all nodes for a story."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        # Create a few nodes
        client.post(f"/api/v1/stories/{story_id}/nodes", json=sample_node_data)
        
        response = client.get(f"/api/v1/stories/{story_id}/nodes")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_get_node_with_children(self, client, sample_story_data, sample_node_data):
        """Test getting a node with its children."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        root_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json=sample_node_data,
        )
        root_id = root_response.json()["id"]
        
        # Create children
        for i in range(2):
            client.post(
                f"/api/v1/stories/{story_id}/nodes",
                json={
                    "content": f"Child node {i}",
                    "choice_text": f"Choice {i}",
                    "parent_id": root_id,
                },
            )
        
        response = client.get(f"/api/v1/stories/{story_id}/nodes/{root_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["children"]) == 2

    def test_delete_node(self, client, sample_story_data, sample_node_data):
        """Test deleting a non-root node."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        root_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json=sample_node_data,
        )
        root_id = root_response.json()["id"]
        
        child_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json={
                "content": "Child node",
                "parent_id": root_id,
            },
        )
        child_id = child_response.json()["id"]
        
        response = client.delete(f"/api/v1/stories/{story_id}/nodes/{child_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cannot_delete_root_node(self, client, sample_story_data, sample_node_data):
        """Test that root nodes cannot be deleted."""
        story_response = client.post("/api/v1/stories/", json=sample_story_data)
        story_id = story_response.json()["id"]
        
        root_response = client.post(
            f"/api/v1/stories/{story_id}/nodes",
            json=sample_node_data,
        )
        root_id = root_response.json()["id"]
        
        response = client.delete(f"/api/v1/stories/{story_id}/nodes/{root_id}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
