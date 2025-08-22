import os
from dotenv import load_dotenv
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import Task

load_dotenv()

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()



@pytest.fixture(scope="function")
def test_db(test_engine):
    connection = test_engine.connect()

    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_tasks(test_db):
    test_db.query(Task).delete()
    test_db.commit()

    tasks = [
        Task(title="Test Task 1", description="Description 1", completed=False),
        Task(title="Test Task 2", description="Description 2", completed=True),
        Task(title="Test Task 3", description="", completed=False),
    ]

    test_db.add_all(tasks)
    test_db.commit()

    for task in tasks:
        test_db.refresh(task)

    return tasks


def test_read_tasks(client, test_tasks):
    response = client.get("/")

    assert response.status_code == 200
    assert "Test Task 1" in response.text
    assert "Test Task 2" in response.text
    assert "Мои задачи" in response.text


def test_create_task(client, test_db):
    response = client.post(
        "/tasks/create",
        data={
            "title": "New Test Task",
            "description": "Test Description",
            "completed": "false"
        },
        follow_redirects=False
    )

    assert response.status_code == 303

    task = test_db.query(Task).filter(Task.title == "New Test Task").first()
    assert task is not None
    assert task.description == "Test Description"


def test_read_task(client, test_tasks):
    task_id = test_tasks[0].id
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert "Test Task 1" in response.text
    assert "Description 1" in response.text


def test_update_task(client, test_tasks, test_db):
    task_id = test_tasks[0].id

    response = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "title": "Updated Task",
            "description": "Updated Description",
            "completed": "true"
        },
        follow_redirects=False
    )

    assert response.status_code == 303

    updated_task = test_db.query(Task).filter(Task.id == task_id).first()
    assert updated_task.title == "Updated Task"
    assert updated_task.description == "Updated Description"
    assert updated_task.completed == True


def test_delete_task(client, test_tasks, test_db):
    task_id = test_tasks[0].id
    initial_count = test_db.query(Task).count()

    response = client.post(f"/tasks/{task_id}/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    final_count = test_db.query(Task).count()
    assert final_count == initial_count - 1

    deleted_task = test_db.query(Task).filter(Task.id == task_id).first()
    assert deleted_task is None


def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


def test_get_tasks_api(client, test_tasks):
    response = client.get("/api/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 3
    assert data["tasks"][0]["title"] == "Test Task 1"


if __name__ == "__main__":
    pytest.main([__file__])