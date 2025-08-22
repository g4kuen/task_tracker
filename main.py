from dotenv import load_dotenv
import os

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session


load_dotenv()

from database import get_db, engine, Base
from models import Task
import crud
from schemas import TaskForm

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo App with PostgreSQL",
    description="CRUD приложение для управления задачами",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")




@app.get("/", response_class=HTMLResponse)
async def read_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tasks": tasks}
    )



@app.get("/tasks/create", response_class=HTMLResponse)
async def create_task_form(request: Request):
    return templates.TemplateResponse(
        "create_task.html",
        {"request": request}
    )



@app.post("/tasks/create", response_class=RedirectResponse)
async def create_task(
        request: Request,
        title: str = Form(...),
        description: str = Form(None),
        completed: bool = Form(False),
        db: Session = Depends(get_db)
):
    task_data = TaskForm(title=title, description=description, completed=completed)
    task = crud.create_task(db, task_data)
    return RedirectResponse(url=f"/tasks/{task.id}", status_code=303)



@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def read_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse(
        "task_detail.html",
        {"request": request, "task": task}
    )



@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_form(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse(
        "update_task.html",
        {"request": request, "task": task}
    )


@app.post("/tasks/{task_id}/edit", response_class=RedirectResponse)
async def update_task(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        completed: bool = Form(False),
        db: Session = Depends(get_db)
):
    task_data = TaskForm(title=title, description=description, completed=completed)
    task = crud.update_task(db, task_id, task_data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return RedirectResponse(url=f"/tasks/{task_id}", status_code=303)



@app.post("/tasks/{task_id}/delete", response_class=RedirectResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return RedirectResponse(url="/", status_code=303)


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Application is running correctly"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/tasks")
async def get_tasks_api(db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return {"tasks": tasks}



@app.get("/api")
async def root():
    return {
        "message": "Todo App API",
        "version": "1.0.0",
        "endpoints": {
            "web_interface": "/",
            "api_docs": "/docs",
            "health_check": "/api/health",
            "tasks_api": "/api/tasks"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )