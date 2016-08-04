from flask import send_from_directory,render_template,url_for,current_app
from . import common_blueprint
from scram_web.config import server_debug
import os


@common_blueprint.route('/logo.png')
def show_logo():
    if server_debug:
        print("Fetchn the Logo...")
    return send_from_directory(os.path.join(common_blueprint.root_path,'static'), filename='img/logo.png')

@common_blueprint.route('/favicon.png')
def show_favicon():
    if server_debug:
        print("Fetchn the Favicon...")
    return send_from_directory(os.path.join(common_blueprint.root_path,'static'), filename='img/favicon.png')

@common_blueprint.route('/bootstrap-custom.css')
def show_bootstrap_kustm_css():
    if server_debug:
        print("Fetchn the Kustom css...")
    return send_from_directory(os.path.join(common_blueprint.root_path,'static'), filename='css/bootstrap-custom.css')

@common_blueprint.route('/404')
def show_error_404():
    if server_debug:
        print("Fetchn the error 404...")
        print(url_for('common.static', filename='img/logo.png'))

    return render_template('404.html')

@common_blueprint.errorhandler(404)
def page_not_found(e):
    return url_for(show_error_404),404