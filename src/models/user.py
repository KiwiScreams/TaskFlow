from src.ext import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.base import BaseModel

class User(BaseModel, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    profile_image = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))


    memberships = db.relationship("WorkspaceMembership", back_populates="user")

    @property
    def password(self):
        raise AttributeError("Password is write-only!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
