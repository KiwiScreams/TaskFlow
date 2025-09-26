from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class WorkspaceForm(FlaskForm):
    name = StringField(
        "Workspace Name",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "Enter workspace name", "class": "form-control rounded-3"}
    )
    color = StringField(
        "Workspace Color",
        validators=[DataRequired(), Length(min=4, max=7)],
        render_kw={"type": "color", "class": "form-control form-control-color rounded-3"}
    )
    submit = SubmitField("Submit", render_kw={"class": "btn btn-gradient rounded-3 py-2 fw-semibold"})


class InviteUserForm(FlaskForm):
    email = StringField("User Email", validators=[DataRequired()])
    submit = SubmitField("Invite")
