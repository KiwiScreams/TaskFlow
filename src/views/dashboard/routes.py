from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.models.workspace_membership import WorkspaceMembership

dashboard_blueprint = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_blueprint.route("/", methods=["GET"])
@login_required
def dashboard():
    memberships = WorkspaceMembership.query.filter_by(user_id=current_user.id).all()
    workspaces = [m.workspace for m in memberships]
    workspace_roles = {m.workspace_id: m.role for m in memberships}

    return render_template(
        "dashboard/dashboard.html",
        workspaces=workspaces,
        workspace_roles=workspace_roles
    )
