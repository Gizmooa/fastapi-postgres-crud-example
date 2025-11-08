import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.constants import API_VERSION_PREFIX


@pytest.mark.integration
class TestCreateNote:
    def test_create_note_success(
        self, client: TestClient, sample_note_data: dict[str, str]
    ):
        response = client.post(f"{API_VERSION_PREFIX}/notes/", json=sample_note_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == sample_note_data["title"]
        assert data["content"] == sample_note_data["content"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_note_minimal(self, client: TestClient):
        response = client.post(
            f"{API_VERSION_PREFIX}/notes/", json={"title": "Minimal Note"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal Note"
        assert data["content"] == ""

    def test_create_note_missing_title(self, client: TestClient):
        response = client.post(
            f"{API_VERSION_PREFIX}/notes/", json={"content": "Some content"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0
        error_locs = [err.get("loc", []) for err in data["detail"]]
        assert any("title" in str(loc).lower() for loc in error_locs)

    def test_create_note_empty_title(self, client: TestClient):
        response = client.post(f"{API_VERSION_PREFIX}/notes/", json={"title": ""})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_note_title_too_long(self, client: TestClient):
        long_title = "a" * 256
        response = client.post(
            f"{API_VERSION_PREFIX}/notes/", json={"title": long_title}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_note_content_too_long(self, client: TestClient):
        long_content = "a" * 10001
        response = client.post(
            f"{API_VERSION_PREFIX}/notes/",
            json={"title": "Test", "content": long_content},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestListNotes:
    def test_list_notes_empty(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_notes_single(self, client: TestClient, sample_note):
        response = client.get(f"{API_VERSION_PREFIX}/notes/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_note.id
        assert data[0]["title"] == sample_note.title

    def test_list_notes_multiple(self, client: TestClient, multiple_notes):
        response = client.get(f"{API_VERSION_PREFIX}/notes/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5
        assert all("id" in note for note in data)
        assert all("title" in note for note in data)

    def test_list_notes_pagination_skip(self, client: TestClient, multiple_notes):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?skip=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_notes_pagination_limit(self, client: TestClient, multiple_notes):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_notes_pagination_both(self, client: TestClient, multiple_notes):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?skip=1&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_notes_invalid_skip(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?skip=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_list_notes_invalid_limit_zero(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?limit=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_list_notes_invalid_limit_too_high(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/?limit=101")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestGetNote:
    def test_get_note_success(self, client: TestClient, sample_note):
        response = client.get(f"{API_VERSION_PREFIX}/notes/{sample_note.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_note.id
        assert data["title"] == sample_note.title
        assert data["content"] == sample_note.content

    def test_get_note_not_found(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_note_invalid_id(self, client: TestClient):
        response = client.get(f"{API_VERSION_PREFIX}/notes/invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestUpdateNote:
    def test_update_note_success(self, client: TestClient, sample_note):
        update_data = {"title": "Updated Title", "content": "Updated Content"}
        response = client.put(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["id"] == sample_note.id

    def test_update_note_requires_title(self, client: TestClient, sample_note):
        """Test that PUT requires title field (content has default)."""
        # Missing title should fail validation
        update_data = {"content": "Only content"}
        response = client.put(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=update_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_note_requires_all_fields(self, client: TestClient, sample_note):
        update_data = {"title": "Updated Title Only"}
        response = client.put(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=update_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0
        error_locs = [err.get("loc", []) for err in data["detail"]]
        assert any("content" in str(loc).lower() for loc in error_locs)

    def test_update_note_not_found(self, client: TestClient):
        update_data = {"title": "New Title", "content": "New Content"}
        response = client.put(f"{API_VERSION_PREFIX}/notes/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_note_invalid_title(self, client: TestClient, sample_note):
        update_data = {"title": "", "content": "Some content"}
        response = client.put(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=update_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.integration
class TestPatchNote:
    def test_patch_note_title_only(self, client: TestClient, sample_note):
        patch_data = {"title": "Patched Title"}
        response = client.patch(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=patch_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == patch_data["title"]
        assert data["content"] == sample_note.content

    def test_patch_note_content_only(self, client: TestClient, sample_note):
        patch_data = {"content": "Patched Content"}
        response = client.patch(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=patch_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == patch_data["content"]
        assert data["title"] == sample_note.title

    def test_patch_note_both_fields(self, client: TestClient, sample_note):
        patch_data = {"title": "New Title", "content": "New Content"}
        response = client.patch(
            f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json=patch_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == patch_data["title"]
        assert data["content"] == patch_data["content"]

    def test_patch_note_empty(self, client: TestClient, sample_note):
        response = client.patch(f"{API_VERSION_PREFIX}/notes/{sample_note.id}", json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == sample_note.title
        assert data["content"] == sample_note.content

    def test_patch_note_not_found(self, client: TestClient):
        patch_data = {"title": "New Title"}
        response = client.patch(f"{API_VERSION_PREFIX}/notes/999", json=patch_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestDeleteNote:
    def test_delete_note_success(self, client: TestClient, sample_note):
        response = client.delete(f"{API_VERSION_PREFIX}/notes/{sample_note.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

        get_response = client.get(f"{API_VERSION_PREFIX}/notes/{sample_note.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_note_not_found(self, client: TestClient):
        response = client.delete(f"{API_VERSION_PREFIX}/notes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_note_twice(self, client: TestClient, sample_note):
        response1 = client.delete(f"{API_VERSION_PREFIX}/notes/{sample_note.id}")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        response2 = client.delete(f"{API_VERSION_PREFIX}/notes/{sample_note.id}")
        assert response2.status_code == status.HTTP_404_NOT_FOUND
