from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_required, current_user
from src import db
from src.models.workspace_membership import WorkspaceMembership
from src.models.user import User
from src.models.task import Task
from src.models.task_status import TaskStatus
from src.views.task.forms import TaskForm
from src.models.workspace import Workspace

task_blueprint = Blueprint("task", __name__, url_prefix="/tasks")


@task_blueprint.route("/create_task", methods=["GET", "POST"])
@login_required
def create_task():
    workspace_id = request.args.get("workspace_id", type=int)
    form = TaskForm()

    user_workspaces = Workspace.query.join(Workspace.memberships).filter_by(user_id=current_user.id).all()
    form.workspace_id.choices = [(w.id, w.name) for w in user_workspaces]

    if workspace_id and workspace_id in [w.id for w in user_workspaces]:
        form.workspace_id.data = workspace_id

    if form.workspace_id.data:
        statuses = TaskStatus.query.filter_by(workspace_id=form.workspace_id.data).all()
        form.status_id.choices = [(s.id, s.name) for s in statuses]

        members = WorkspaceMembership.query.filter_by(workspace_id=form.workspace_id.data).all()
        form.users.choices = [(m.user.id, m.user.username) for m in members]

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            workspace_id=form.workspace_id.data,
            status_id=form.status_id.data
        )
        db.session.add(task)
        db.session.commit()

        if form.users.data:
            task.users = User.query.filter(User.id.in_(form.users.data)).all()
            db.session.commit()

        flash("Task created successfully!", "success")
        return redirect(url_for("workspace.view", workspace_id=form.workspace_id.data))

    return render_template("task/create_task.html", form=form)


@task_blueprint.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.id not in [m.user_id for m in task.workspace.memberships]:
        flash("You do not have permission to edit this task.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    form = TaskForm(obj=task)

    user_workspaces = Workspace.query.join(Workspace.memberships).filter_by(user_id=current_user.id).all()
    form.workspace_id.choices = [(w.id, w.name) for w in user_workspaces]

    if form.workspace_id.data:
        statuses = TaskStatus.query.filter_by(workspace_id=form.workspace_id.data).all()
        form.status_id.choices = [(s.id, s.name) for s in statuses]

        members = WorkspaceMembership.query.filter_by(workspace_id=form.workspace_id.data).all()
        form.users.choices = [(m.user.id, m.user.username) for m in members]

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.workspace_id = form.workspace_id.data
        task.status_id = form.status_id.data

        if form.users.data:
            task.users = User.query.filter(User.id.in_(form.users.data)).all()
        else:
            task.users = []

        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("workspace.view", workspace_id=task.workspace_id))

    form.users.data = [u.id for u in task.users]
    return render_template("task/create_task.html", form=form, edit=True)


@task_blueprint.route("/delete/<int:task_id>", methods=["GET"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    workspace_id = task.workspace_id
    if current_user.id not in [m.user_id for m in task.workspace.memberships]:
        flash("You do not have permission to delete this task.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for("workspace.view", workspace_id=workspace_id))
