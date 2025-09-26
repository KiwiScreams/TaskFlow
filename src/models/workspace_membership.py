from src.ext import db
from src.models.base import BaseModel

class WorkspaceMembership(BaseModel):
    __tablename__ = "workspace_memberships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)

    role = db.Column(db.String(20), default="contributor")

    user = db.relationship("User", back_populates="memberships")
    workspace = db.relationship("Workspace", back_populates="memberships")
