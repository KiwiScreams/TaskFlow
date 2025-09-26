from os import path
import secrets

class Config(object):
    BASE_DIRECTORY = path.abspath(path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SECRET_KEY = secrets.token_hex(32)
    UPLOAD_PATH = path.join(BASE_DIRECTORY, "static", "upload")
    FLASK_ADMIN_SWATCH = "journal"

