from src.ext import db
from src.models.base import BaseModel
from src.models.task_assignment import task_assignments


class Task(BaseModel):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())

    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    workspace = db.relationship("Workspace", back_populates="tasks")

    status_id = db.Column(db.Integer, db.ForeignKey("task_statuses.id"), nullable=False)
    status = db.relationship("TaskStatus", back_populates="tasks")

    users = db.relationship("User", secondary=task_assignments, backref="tasks")
