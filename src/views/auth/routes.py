from uuid import uuid4
from os import path, makedirs
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, redirect, request, flash, url_for
from src.views.auth.forms import RegisterForm, LoginForm
from src.config import Config
from src.models import User
import logging
from datetime import date
from flask_login import login_user, logout_user, login_required, current_user


auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        file = form.profile_image.data
        filename = None

        if file and file.filename:
            _, extension = path.splitext(file.filename)
            filename = f"{uuid4()}{extension}"
            filename = secure_filename(filename)
            makedirs(Config.UPLOAD_PATH, exist_ok=True)
            file_path = path.join(Config.UPLOAD_PATH, filename)
            file.save(file_path)

        new_user = User(
            username=form.username.data,
            password=form.password.data,
            profile_image=filename or "default-user.png",
            email=form.email.data,
            birthday=form.birthday.data,
            gender=form.gender.data,
        )
        new_user.create()
        flash("Registration successful! Please log in.", "success")
        return redirect("/login")

    if form.errors:
        logging.error("Form errors: %s", form.errors)
        flash("Please fix the errors in the form.", "danger")

    return render_template("auth/register.html", form=form)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            flash("Welcome back!", "success")
            return redirect("/")
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)



@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect("/login")


@auth_blueprint.route("/profile")
@login_required
def view_profile():
    today = date.today()
    is_birthday = (
            current_user.birthday.day == today.day and
            current_user.birthday.month == today.month
    )

    return render_template(
        "auth/view_profile.html",
        user=current_user,
        is_birthday=is_birthday
    )