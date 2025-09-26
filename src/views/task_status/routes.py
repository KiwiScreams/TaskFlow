from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src import db
from src.models.task_status import TaskStatus
from src.models.workspace import Workspace
from src.models.task import Task
from src.views.task_status.forms import StatusForm

status_blueprint = Blueprint("status", __name__, url_prefix="/statuses")


@status_blueprint.route("/manage/<int:workspace_id>", methods=["GET", "POST"])
@login_required
def manage_statuses(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    if current_user.id not in [m.user_id for m in workspace.memberships]:
        flash("You do not have access to this workspace", "danger")
        return redirect(url_for("dashboard.dashboard"))

    edit_id = request.args.get("edit_id", type=int)
    if edit_id:
        status = TaskStatus.query.get_or_404(edit_id)
        form = StatusForm(obj=status)
        edit = True
    else:
        form = StatusForm()
        status = None
        edit = False

    if form.validate_on_submit():
        if edit:
            status.name = form.name.data
            flash("Status updated successfully!", "success")
        else:
            status = TaskStatus(name=form.name.data, workspace_id=workspace.id)
            db.session.add(status)
            flash(f"Status '{form.name.data}' added!", "success")
        db.session.commit()
        return redirect(url_for("status.manage_statuses", workspace_id=workspace.id))

    statuses = TaskStatus.query.filter_by(workspace_id=workspace.id).all()
    return render_template(
        "status/manage_statuses.html",
        form=form,
        statuses=statuses,
        workspace=workspace,
        edit=edit
    )


@status_blueprint.route("/delete/<int:status_id>", methods=["GET"])
@login_required
def delete_status(status_id):
    status = TaskStatus.query.get_or_404(status_id)
    workspace_id = status.workspace_id

    tasks_using_status = Task.query.filter_by(status_id=status.id).all()
    if tasks_using_status:
        flash("Cannot delete this status because some tasks are using it!", "danger")
        return redirect(url_for("status.manage_statuses", workspace_id=workspace_id))

    db.session.delete(status)
    db.session.commit()
    flash("Status deleted successfully!", "success")
    return redirect(url_for("status.manage_statuses", workspace_id=workspace_id))
