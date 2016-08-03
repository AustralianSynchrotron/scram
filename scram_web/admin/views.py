from flask import render_template,abort
from jinja2 import TemplateNotFound
from . import admin_blueprint

@admin_blueprint.route('/<page>')
def show_page(page):
    try:
        #return "<h1>/admin/%s</h1>" % page # TODO: render_template
        return render_template('login.html')
    except TemplateNotFound:
        abort(404)