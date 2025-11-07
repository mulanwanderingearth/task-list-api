from flask import Blueprint, abort, make_response, request, Response
from ..db import db
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model
from datetime import datetime
import requests
import os

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


@bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)


@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    sort_quaram = request.args.get("sort")
    if sort_quaram == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_quaram == "desc":
        query = query.order_by(Task.title.desc())

    tasks = db.session.scalars(query)

    if not tasks:
        return {"details": "No tasks found"}, 404

    return [task.to_dict() for task in tasks]


@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict_with_goal_id()


@bp.put("/<task_id>")
def update_one_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()
    
    if not request_body:
        return {"details": "Invalid data"}, 400
    
    task.title = request_body.get("title")
    task.description = request_body.get("description")
    task.completed_at = request_body.get("completed_at")

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("/<task_id>")
def delete_one_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    db.session.commit()

    token = os.environ.get("slack_token")
    response = requests.post(
        url="https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json={"channel": "task-notifications",
              "text": f"Someone just completed the task {task.title}"})

    return Response(status=204, mimetype="application/json")


@bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")
