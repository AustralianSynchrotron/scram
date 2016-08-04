from flask import Flask
import flask_bootstrap
from .admin.views import admin_blueprint
from .common.views import common_blueprint
from config import server_debug

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
if server_debug:
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# Register blueprints
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(common_blueprint, url_prefix='/common')

# Specify local files for local networks
flask_bootstrap.StaticCDN(static_endpoint='/static')

# Send the app to Bootstrap
flask_bootstrap.Bootstrap(app)

if server_debug:
    print(app.url_map)

from . import views