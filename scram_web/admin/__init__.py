from flask import Blueprint

admin_blueprint = Blueprint('admin',__name__,
                            template_folder='templates',
                            static_folder='static')

from . import views
