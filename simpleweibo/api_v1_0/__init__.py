from flask import Blueprint

api = Blueprint('api',__name__)

from simpleweibo.api_v1_0 import models