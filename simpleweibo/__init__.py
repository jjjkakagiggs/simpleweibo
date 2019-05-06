import os
import click

from flask import Flask
from flask_login import current_user
from simpleweibo.extensions import bootstrap, db, login_manager, mail, whooshee, avatars, csrf,migrate
from simpleweibo.settings import config
from simpleweibo.models import User,Role,Post,Comment,Permission
from simpleweibo.api_v1_0 import api as api_v1_0_buleprint
from simpleweibo.auth import auth as auth_buleprint
from simpleweibo.main import main as main_buleprint


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG','development')

    app = Flask('simpleweibo')

    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    whooshee.init_app(app)
    migrate.init_app(app,db)
    register_shell_context(app)
    register_template_context(app)
    register_template_context(app)
    register_blueprints(app)
    register_commands(app)


    return app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db,
                    User=User,
                    Role=Role,
                    Post=Post,
                    Comment=Comment)

def register_template_context(app):
    """
    注入全局变量，在 jinja2 模板中可用
    """
    @app.context_processor
    def make_template_context():
        return dict(Permission=Permission,
                    current_user=current_user)


def register_blueprints(app):
    app.register_blueprint(main_buleprint)
    app.register_blueprint(auth_buleprint,url_prefix='/auth')
    app.register_blueprint(api_v1_0_buleprint, url_prefix='/api/v1.0')


def register_commands(app):
    @app.cli.command()
    def forge():
        from simpleweibo.fakes import fake_admin,faker_user,faker_post,faker_comment
        click.echo('data initing ing.....')
        Role.init_role()
        fake_admin()
        faker_user()
        faker_post()
        faker_comment()
        click.echo('Done....!')



