from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager,AnonymousUserMixin
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_whooshee import Whooshee

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()
avatars = Avatars()
whooshee = Whooshee()


# @login_manager.user_loader
# def login_user(user_id):
#     """ Flask-Login 回调函数，用于指定标识符加载用户
#        :param user_id: 用户 id
#        :current_user
#        :return: 查询到的用户对象
#        """
#     from simpleweibo.models import User
#     user = User.query.get(int(user_id))
#     return user
#
#
# login_manager.login_view = 'auth.login'
# login_manager.login_message_category = 'warning'
#
# login_manager.refresh_view = 'auth.re_authenticate'
# login_manager.needs_refresh_message_category = 'warning'
#
#
# class Guest(AnonymousUserMixin):
#     def can(self,perssion_name):
#         """ 游客没有任何权限
#                 :param permissions: 指定权限
#                 :return: 无任何权限
#                 """
#         return False
#
#     @property
#     def is_adim(self):
#         """ 判断是或否为管理员
#                 :return: 非管理员
#                 """
#         return False