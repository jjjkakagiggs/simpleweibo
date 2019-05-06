from flask import Blueprint

auth = Blueprint('auth',__name__)

from simpleweibo.auth import views