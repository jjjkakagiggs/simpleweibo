import os
# import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


PASSWORD = os.getenv('password')
HOST = os.getenv('host')
PORT = os.getenv('port')

class BaseConfig():
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Simple_weibo', MAIL_USERNAME)

    ADMIN_EMAIL = os.getenv('WEIBO_EMAIL')
    POST_PER_PAGE = 10
    MANAGE_POST_PER_PAGE = 15
    COMMENT_PER_PAGE = 15
    FLASK_MAIL_SUBJECT_PREFIX = '[简微博]'

    THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}
    SLOW_QUERY_THRESHOLD = 1

    UPLOAD_PATH = os.path.join(basedir, 'uploads_weibo')



class DevelopmentConfig(BaseConfig):
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = 'root'
    PASSWORD = PASSWORD
    HOST = HOST
    PORT = PORT
    DATABASE = 'simpleweibo_dev'
    SQLALCHEMY_DATABASE_URI = r"{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST,
                                                                            PORT, DATABASE)


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = 'root'
    PASSWORD = PASSWORD
    HOST = HOST
    PORT = PORT
    DATABASE = 'simpleweibo_test'
    SQLALCHEMY_DATABASE_URI = r"{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST,
                                                                            PORT, DATABASE)


class ProductionConfig(BaseConfig):
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = 'root'
    PASSWORD = PASSWORD
    HOST = HOST
    PORT = PORT
    DATABASE = 'simpleweibo_pro'
    SQLALCHEMY_DATABASE_URI = r"{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST,
                                                                            PORT, DATABASE)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
