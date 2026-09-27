import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.models.audio import AudioFile, SourceType
from app.models.transcription import Transcription, TranscriptionStatus
from app.models.review import HumanReview, ReviewStatus
from app.core.security import get_password_hash

# Test database - use file-based for proper isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_review.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    """Create a user and return auth token."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def audio_id(client, auth_token):
    """Upload an audio file and return its ID."""
    audio_content = b"fake audio data for review testing"
    audio_file = io.BytesIO(audio_content)
    audio_file.name = "test_audio.mp3"
    
    files = {"file": ("test_audio.mp3", audio_file, "audio/mpeg")}
    
    response = client.post(
        "/api/v1/audio/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    return response.json()["id"]


@pytest.fixture
def transcription_id(client, auth_token, audio_id):
    """Create a transcription and return its ID."""
    response = client.post(
        "/api/v1/speech/transcribe",
        json={"audio_id": audio_id},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    return response.json()["id"]


def test_create_review(client, auth_token, transcription_id):
    """Test creating a human review for a transcription."""
    original_ai_text = "This is the original AI transcription"
    
    # First, get the original transcription to verify AI text
    get_response = client.get(
        f"/api/v1/speech/transcriptions/{transcription_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    original_ai_transcription = get_response.json()["ai_transcription"]
    
    # Create a review
    response = client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "This is the corrected human transcription",
            "review_notes": "Fixed grammar and spelling"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["transcription_id"] == transcription_id
    assert data["corrected_text"] == "This is the corrected human transcription"
    assert data["review_notes"] == "Fixed grammar and spelling"
    assert data["status"] == "reviewed"
    
    # Verify original AI transcription was NOT modified
    get_response_after = client.get(
        f"/api/v1/speech/transcriptions/{transcription_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response_after.json()["ai_transcription"] == original_ai_transcription


def test_create_review_without_auth(client, transcription_id):
    """Test creating a review without authentication."""
    response = client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "Corrected text"
        }
    )
    assert response.status_code == 401


def test_create_review_invalid_transcription(client, auth_token):
    """Test creating a review for non-existent transcription."""
    response = client.post(
        "/api/v1/transcriptions/99999/review",
        json={
            "transcription_id": 99999,
            "corrected_text": "Corrected text"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_create_review_id_mismatch(client, auth_token, transcription_id):
    """Test creating a review with ID mismatch."""
    response = client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": 99999,  # Different from URL
            "corrected_text": "Corrected text"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400


def test_get_review(client, auth_token, transcription_id):
    """Test getting an existing review."""
    # First create a review
    client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "Corrected text",
            "review_notes": "Notes"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get the review
    response = client.get(
        f"/api/v1/transcriptions/{transcription_id}/review",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["transcription_id"] == transcription_id
    assert data["corrected_text"] == "Corrected text"
    assert data["review_notes"] == "Notes"


def test_get_review_without_auth(client, transcription_id):
    """Test getting a review without authentication."""
    response = client.get(f"/api/v1/transcriptions/{transcription_id}/review")
    assert response.status_code == 401


def test_get_review_not_found(client, auth_token, transcription_id):
    """Test getting a review that doesn't exist."""
    response = client.get(
        f"/api/v1/transcriptions/{transcription_id}/review",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_update_review(client, auth_token, transcription_id):
    """Test updating an existing review."""
    # First create a review
    client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "Original corrected text",
            "review_notes": "Original notes"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Update the review
    response = client.patch(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "corrected_text": "Updated corrected text",
            "review_notes": "Updated notes"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["corrected_text"] == "Updated corrected text"
    assert data["review_notes"] == "Updated notes"


def test_update_review_without_existing(client, auth_token, transcription_id):
    """Test updating a review that doesn't exist."""
    response = client.patch(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "corrected_text": "Updated text"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_update_review_without_auth(client, transcription_id):
    """Test updating a review without authentication."""
    response = client.patch(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={"corrected_text": "Updated text"}
    )
    assert response.status_code == 401


def test_ai_transcription_integrity_after_review(client, auth_token, transcription_id):
    """Test that original AI transcription remains unchanged after review."""
    # Get original AI transcription
    get_before = client.get(
        f"/api/v1/speech/transcriptions/{transcription_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    original_ai_text = get_before.json()["ai_transcription"]
    
    # Create a review
    client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "Completely different text",
            "review_notes": "Changed everything"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Verify AI transcription is still the same
    get_after = client.get(
        f"/api/v1/speech/transcriptions/{transcription_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_after.json()["ai_transcription"] == original_ai_text


def test_review_without_notes(client, auth_token, transcription_id):
    """Test creating a review without optional notes."""
    response = client.post(
        f"/api/v1/transcriptions/{transcription_id}/review",
        json={
            "transcription_id": transcription_id,
            "corrected_text": "Corrected text"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["corrected_text"] == "Corrected text"
    assert data["review_notes"] is None
