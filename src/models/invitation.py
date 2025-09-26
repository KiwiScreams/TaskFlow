from datetime import datetime
from src.ext import db
from src.models.base import BaseModel

class Invitation(BaseModel):
    __tablename__ = "invitations"

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workspace = db.relationship("Workspace", backref="invitations")
    user = db.relationship("User", foreign_keys=[user_id])
    inviter = db.relationship("User", foreign_keys=[inviter_id])
