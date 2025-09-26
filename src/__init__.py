from flask import Flask
from src.commands import init_db_command, populate_db_command
from src.config import Config
from src.ext import db, migrate, login_manager
from src.views import main_blueprint, auth_blueprint, workspace_blueprint, dashboard_blueprint, task_blueprint, status_blueprint
from src.models import User
from src.models import Task
from src.models import WorkspaceMembership
from src.models import Workspace
from src.models import TaskStatus

BLUEPRINTS = [main_blueprint, auth_blueprint, workspace_blueprint, dashboard_blueprint, task_blueprint, status_blueprint]
COMMANDS = [init_db_command, populate_db_command]

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(_id):
        return User.query.get(_id)

def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

def register_commands(app):
    for command in COMMANDS:
        app.cli.add_command(command)