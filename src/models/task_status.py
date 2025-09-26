from src.ext import db
from src.models.base import BaseModel

class TaskStatus(BaseModel):
    __tablename__ = "task_statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20))

    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    workspace = db.relationship("Workspace", back_populates="statuses")

    tasks = db.relationship("Task", back_populates="status")
