from flask import Blueprint

common_blueprint = Blueprint('common',__name__,
                            template_folder='templates',
                            static_folder='static')

from . import views