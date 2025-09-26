from datetime import date
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from string import ascii_uppercase, ascii_lowercase, digits, punctuation
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, RadioField, FileField
from wtforms.fields import EmailField
from flask_wtf.file import FileAllowed, FileSize
from src.models.user import User

class RegisterForm(FlaskForm):
    username = StringField("Enter username",
                           validators=[DataRequired(message='Please enter your username')])
    email = EmailField("Enter email",
                       validators=[DataRequired(message='Please enter your email')])
    password = PasswordField("Enter password",
                             validators=[DataRequired(message='Please enter your password'),
                                         Length(min=8, max=64)])
    repeat_password = PasswordField("Repeat password",
                                    validators=[DataRequired(message='Please confirm your password'),
                                                EqualTo("password",
                                                        message="Passwords must match.")])
    birthday = DateField("Enter birthday",
                         format="%Y-%m-%d",
                         validators=[DataRequired(message='Please enter your birthday')])
    gender = RadioField("Choose gender", choices=[(0, "Male"), (1, "Female")],
                        validators=[DataRequired(message='Please choose your gender')])
    profile_image = FileField("Upload Profile Image",
                              validators=[FileSize(1024 * 1024),
                                          FileAllowed(["jpg", "png", "jpeg"])])
    submit = SubmitField("Sign Up")

    def validate_password(self, field):
        contains_uppercase = any(c in ascii_uppercase for c in field.data)
        contains_lowercase = any(c in ascii_lowercase for c in field.data)
        contains_digits = any(c in digits for c in field.data)
        contains_symbols = any(c in punctuation for c in field.data)

        if not contains_uppercase:
            raise ValidationError("Password must contain at least one uppercase letter")
        if not contains_lowercase:
            raise ValidationError("Password must contain at least one lowercase letter")
        if not contains_digits:
            raise ValidationError("Password must contain at least one digit (0-9)")
        if not contains_symbols:
            raise ValidationError("Password must contain at least one special character (e.g., !, @, #, etc.)")

    def validate_birthday(self, field):
        today = date.today()
        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        if age < 18:
            raise ValidationError("You must be at least 18 years old to register.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("This email is already registered.")



class LoginForm(FlaskForm):
    email = StringField(
        "Enter email",
        validators=[DataRequired(message="Email is required")])
    password = PasswordField(
        "Enter password",
        validators=[DataRequired(message="Password is required")])
    login = SubmitField("Login")
