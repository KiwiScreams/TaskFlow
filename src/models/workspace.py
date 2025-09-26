from datetime import datetime
from src.ext import db
from src.models.base import BaseModel

class Workspace(BaseModel):
    __tablename__ = "workspaces"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.String(7), default="#FFFFFF")

    memberships = db.relationship("WorkspaceMembership", back_populates="workspace")
    statuses = db.relationship("TaskStatus", back_populates="workspace", cascade="all, delete-orphan")
    tasks = db.relationship("Task", back_populates="workspace", cascade="all, delete-orphan")

