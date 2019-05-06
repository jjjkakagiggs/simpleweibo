from flask import Blueprint

main = Blueprint('main',__name__)

from simpleweibo.main import views,errors