from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.ext import db
from src.models import User, WorkspaceMembership, Workspace, Invitation, Task
from .forms import WorkspaceForm, InviteUserForm

workspace_blueprint = Blueprint("workspace", __name__, url_prefix="/workspace")
@workspace_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = WorkspaceForm()
    if form.validate_on_submit():
        workspace = Workspace(name=form.name.data, color=form.color.data)
        db.session.add(workspace)
        db.session.commit()

        membership = WorkspaceMembership(
            user_id=current_user.id,
            workspace_id=workspace.id,
            role="admin"
        )
        db.session.add(membership)
        db.session.commit()

        flash("Workspace created successfully!", "success")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    return render_template("workspace/create_workspace.html", form=form)


@workspace_blueprint.route("/<int:workspace_id>")
@login_required
def view(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    membership = WorkspaceMembership.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()
    if not membership:
        flash("You don’t have access to this workspace.", "danger")
        return redirect("/dashboard")

    status_filter = request.args.get("status_id", "all")

    if status_filter == "all":
        tasks = Task.query.filter_by(workspace_id=workspace.id).all()
    else:
        tasks = Task.query.filter_by(
            workspace_id=workspace.id, status_id=int(status_filter)
        ).all()

    members = WorkspaceMembership.query.filter_by(workspace_id=workspace.id).all()

    return render_template(
        "workspace/view_workspace.html",
        workspace=workspace,
        tasks=tasks,
        members=members,
        selected_status=status_filter,
        membership=membership

    )


@workspace_blueprint.route("/<int:workspace_id>/delete", methods=["GET"])
@login_required
def delete(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    membership = WorkspaceMembership.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()

    if not membership:
        flash("You don’t have access to this workspace.", "danger")
        return redirect("/dashboard")

    if membership.role != "admin":
        flash("Only admins can delete this workspace.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    # Delete all related rows first
    Task.query.filter_by(workspace_id=workspace.id).delete()
    WorkspaceMembership.query.filter_by(workspace_id=workspace.id).delete()
    Invitation.query.filter_by(workspace_id=workspace.id).delete()  # <- delete invitations first

    # Then delete workspace
    db.session.delete(workspace)
    db.session.commit()

    flash("Workspace deleted successfully!", "success")
    return redirect("/dashboard")



@workspace_blueprint.route("/<int:workspace_id>/edit", methods=["GET", "POST"])
@login_required
def edit(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    membership = WorkspaceMembership.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()

    if not membership:
        flash("You don’t have access to this workspace.", "danger")
        return redirect("/dashboard")

    if membership.role != "admin":
        flash("Only admins can edit this workspace.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    form = WorkspaceForm(obj=workspace)

    if form.validate_on_submit():
        workspace.name = form.name.data
        workspace.color = form.color.data
        db.session.commit()

        flash("Workspace updated successfully!", "success")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    return render_template("workspace/create_workspace.html", form=form, workspace=workspace)


@workspace_blueprint.route("/<int:workspace_id>/invite", methods=["GET", "POST"])
@login_required
def invite_user(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    membership = WorkspaceMembership.query.filter_by(
        workspace_id=workspace.id, user_id=current_user.id, role="admin"
    ).first()
    if not membership:
        flash("Only admins can invite users.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    form = InviteUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("User not found. Make sure they are registered.", "danger")
        else:
            # check if already invited
            existing = Invitation.query.filter_by(
                workspace_id=workspace.id, user_id=user.id, status="pending"
            ).first()
            if existing:
                flash("User already has a pending invitation.", "warning")
            else:
                invite = Invitation(
                    workspace_id=workspace.id,
                    user_id=user.id,
                    inviter_id=current_user.id,   # <- FIXED
                    status="pending"
                )
                db.session.add(invite)
                db.session.commit()
                flash(f"{user.username} has been invited!", "success")
                return redirect(url_for("workspace.view", workspace_id=workspace.id))

    return render_template("workspace/invite_user.html", form=form, workspace=workspace)



@workspace_blueprint.route("/invitations")
@login_required
def invitations():
    received_invites = Invitation.query.filter_by(user_id=current_user.id).all()

    sent_invites = Invitation.query.filter_by(inviter_id=current_user.id).all()

    return render_template("workspace/invitations.html",
                           received_invites=received_invites,
                           sent_invites=sent_invites)


@workspace_blueprint.route("/invitations/<int:invite_id>/accept")
@login_required
def accept_invite(invite_id):
    invite = Invitation.query.get_or_404(invite_id)

    if invite.user_id != current_user.id:
        flash("You cannot accept this invitation.", "danger")
        return redirect(url_for("workspace.invitations"))

    membership = WorkspaceMembership.query.filter_by(
        workspace_id=invite.workspace_id, user_id=current_user.id
    ).first()

    if not membership:
        new_member = WorkspaceMembership(
            workspace_id=invite.workspace_id,
            user_id=current_user.id,
            role="contributor"
        )
        db.session.add(new_member)

    invite.status = "accepted"
    db.session.commit()

    flash("You’ve joined the workspace!", "success")
    return redirect(url_for("workspace.view", workspace_id=invite.workspace_id))



@workspace_blueprint.route("/<int:workspace_id>/remove_member/<int:user_id>", methods=["POST", "GET"])
@login_required
def remove_member(workspace_id, user_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    membership = WorkspaceMembership.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()
    if not membership or membership.role != "admin":
        flash("Only admins can remove members.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    if user_id == current_user.id:
        flash("You cannot remove yourself as admin.", "warning")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    member_to_remove = WorkspaceMembership.query.filter_by(
        workspace_id=workspace.id, user_id=user_id
    ).first()

    if not member_to_remove:
        flash("User is not a member of this workspace.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    if member_to_remove.role == "admin":
        flash("You cannot remove another admin.", "danger")
        return redirect(url_for("workspace.view", workspace_id=workspace.id))

    db.session.delete(member_to_remove)
    db.session.commit()

    flash("Member removed successfully.", "success")
    return redirect(url_for("workspace.view", workspace_id=workspace.id))
