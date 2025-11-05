from flask import Blueprint,abort, make_response,request,Response
from ..db import db
from app.models.task import Task
from app.routes.route_utilities import validate_model
from datetime import datetime
import requests
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

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
    sort_quaram = request.args.get("sort")
    if sort_quaram =="asc" :
        query = query.order_by(Task.title.asc())
    elif sort_quaram == "desc":
         query = query.order_by(Task.title.desc())

    tasks = db.session.scalars(query)

    if not tasks:
         return {"details": "No tasks found"}, 404
    
    return [task.to_dict() for task in tasks]


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()

@tasks_bp.put("/<task_id>")
def update_one_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()
    task.title = request_body.get("title")
    task.description = request_body.get("description")
    task.completed_at = request_body.get("completed_at")

    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.delete("/<task_id>")
def delete_one_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    db.session.commit()

    token = os.environ.get("slack_token")
    response = requests.post(
        url="https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json={"channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}" })
    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")