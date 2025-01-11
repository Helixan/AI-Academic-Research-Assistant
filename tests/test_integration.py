import os
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.utils.config import load_config
from src.database.database import Base, get_db

config = load_config()

if "test_database" in config and "url" in config["database"]:
    os.environ["TEST_DATABASE_URL"] = config["test_database"]["url"]

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Academic Research Assistant API"}


def test_create_user():
    payload = {"username": "alice", "email": "alice@example.com", "password": "secret123"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "alice"


def test_list_users():
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == "alice"


def test_upload_paper(tmp_path):
    pdf_file = tmp_path / "test_paper.pdf"
    c = canvas.Canvas(str(pdf_file))
    c.drawString(72, 72, "Hello from a valid PDF!")
    c.showPage()
    c.save()

    with open(pdf_file, "rb") as f:
        file_bytes = f.read()

    files = {
        "file": ("test_paper.pdf", file_bytes, "application/pdf")
    }
    data = {
        "title": "Test Paper",
        "abstract": "Testing abstract"
    }

    response = client.post("/papers/", files=files, data=data)
    assert response.status_code == 200, response.text

    paper_data = response.json()
    assert paper_data["title"] == "Test Paper"
    assert paper_data["abstract"] == "Testing abstract"
    assert "id" in paper_data

    list_response = client.get("/papers/")
    assert list_response.status_code == 200
    papers_list = list_response.json()
    assert len(papers_list) == 1
    assert papers_list[0]["title"] == "Test Paper"


def test_summarize_paper():
    response = client.post("/papers/summarize/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "summary" in data


def test_search_papers():
    response = client.get("/papers/search?query=Test")
    assert response.status_code == 200, response.text
    results_data = response.json()
    assert "results" in results_data
    assert isinstance(results_data["results"], list)
