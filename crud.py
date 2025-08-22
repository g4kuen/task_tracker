from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from schemas import TaskCreate, TaskUpdate
from models import Task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session,
              skip: int = 0,
              limit: int = 100,
              completed: Optional[bool] = None) -> List[Task]:
    query = db.query(Task)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    return query.order_by(desc(Task.created_at)).offset(skip).limit(limit).all()


def get_tasks_count(db: Session, completed: Optional[bool] = None) -> int:
    query = db.query(Task)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    return query.count()


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def update_task(db: Session,
                task_id: int,
                task: TaskUpdate) -> Optional[Task]:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        # Обновляем только переданные поля
        if task.title is not None:
            db_task.title = task.title
        if task.description is not None:
            db_task.description = task.description
        if task.completed is not None:
            db_task.completed = task.completed

        db.commit()
        db.refresh(db_task)

    return db_task


def delete_task(db: Session, task_id: int) -> Optional[Task]:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        db.delete(db_task)
        db.commit()

    return db_task


def toggle_task_completion(db: Session, task_id: int) -> Optional[Task]:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        db_task.completed = not db_task.completed
        db.commit()
        db.refresh(db_task)

    return db_task


def search_tasks(db: Session,
                 search_term: str,
                 limit: int = 50) -> List[Task]:
    return db.query(Task).filter(
        (Task.title.ilike(f"%{search_term}%")) |
        (Task.description.ilike(f"%{search_term}%"))
    ).order_by(desc(Task.created_at)).limit(limit).all()


def get_recent_tasks(db: Session, limit: int = 10) -> List[Task]:
    return db.query(Task).order_by(desc(Task.created_at)).limit(limit).all()


def get_completed_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return get_tasks(db, skip=skip, limit=limit, completed=True)


def get_pending_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return get_tasks(db, skip=skip, limit=limit, completed=False)


def bulk_create_tasks(db: Session, tasks: List[TaskCreate]) -> List[Task]:
    db_tasks = []

    for task_data in tasks:
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed
        )
        db.add(db_task)
        db_tasks.append(db_task)

    db.commit()

    for db_task in db_tasks:
        db.refresh(db_task)

    return db_tasks


def bulk_delete_tasks(db: Session, task_ids: List[int]) -> int:
    result = db.query(Task).filter(Task.id.in_(task_ids)).delete()
    db.commit()
    return result


def bulk_update_tasks_completion(db: Session, task_ids: List[int], completed: bool) -> int:
    result = db.query(Task).filter(Task.id.in_(task_ids)).update(
        {"completed": completed},
        synchronize_session=False
    )
    db.commit()
    return result