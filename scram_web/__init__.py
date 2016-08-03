from flask import Flask
import flask_bootstrap
from .admin.views import admin_blueprint

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# Register blueprints
app.register_blueprint(admin_blueprint,url_prefix='/admin')

# Specify local files for local networks
flask_bootstrap.StaticCDN(static_endpoint='/static')

# Send the app to Bootstrap
flask_bootstrap.Bootstrap(app)

#import scram_web.config
#import scram_web.views