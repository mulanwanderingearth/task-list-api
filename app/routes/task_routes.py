from flask import Blueprint,abort, make_response, request,Response
from ..db import db
tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
from app.models.task import Task

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    
    try:
        title = request_body["title"]
        description = request_body["description"]
    except KeyError:
        return {"details": "Invalid data"}, 400
    
    completed_at = request_body.get("completed_at")
    
    new_task = Task.from_dict(
        request_body
    )
    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)
    tasks = db.session.scalars(query)

    if not tasks:
         return {"details": "No tasks found"}, 404
    
    return [task.to_dict() for task in tasks]


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)
    return task.to_dict()

@tasks_bp.put("/<task_id>")
def update_one_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()
    task.title = request_body.get("title")
    task.description = request_body.get("description")
    task.completed_at = request_body.get("completed_at")

    db.session.commit()

    return Response(status=204, mimetype="application/json")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"details": f"task {task_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"details": f"Task {task_id} not found"}
        abort(make_response(response, 404))

    return task

@tasks_bp.delete("/<task_id>")
def delete_one_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
