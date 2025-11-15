from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.task import Task
from ..db import db


class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }

    def to_dict_with_tasks(self):
        dict_with_tasks = Goal.to_dict(self)
        dict_with_tasks["tasks"] = [task.to_dict() for task in self.tasks]
        
        return dict_with_tasks

    @classmethod
    def from_dict(cls, goal_data):
        return cls(title=goal_data["title"])
