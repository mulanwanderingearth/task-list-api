from flask import Blueprint, abort, make_response, request, Response
from app.db import db
from app.models.goal import Goal
from app.models.task import Task
from app.routes.route_utilities import validate_model, create_model
import requests
import os

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@bp.post("")
def create_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)


@bp.get("")
# need to refactor later
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goals = db.session.scalars(query)
    return [goal.to_dict() for goal in goals]


@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict()


@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    
    if not request_body or "title" not in request_body:
        return {"details": "Invalid data"}, 400
    
    goal.title = request_body["title"]
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@bp.delete("/<goal_id>")
def delete_goal_by_id(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@bp.post("/<goal_id>/tasks")
def update_tasks_by_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal.tasks.clear()
    request_body = request.get_json()
    task_id_list = request_body["task_ids"]

    for id in task_id_list:
        task = validate_model(Task, id)
        task.goal_id = goal_id

    db.session.commit()

    return {"id": goal.id,
            "task_ids": task_id_list}


@bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return goal.to_dict_with_tasks()
