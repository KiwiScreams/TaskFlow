from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from src.models.workspace import Workspace

class TaskForm(FlaskForm):
    title = StringField(
        "Task Title",
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={"placeholder": "Enter task title", "class": "form-control"}
    )
    description = TextAreaField(
        "Task Description",
        validators=[Length(max=3000)],
        render_kw={"placeholder": "Enter task description (optional)", "class": "form-control", "rows": 4}
    )
    workspace_id = SelectField(
        "Workspace",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    status_id = SelectField("Status", coerce=int, validators=[DataRequired()])
    users = SelectMultipleField("Assign Users", coerce=int)
    submit = SubmitField(
        "Submit",
        render_kw={"class": "btn btn-primary w-100"}
    )
