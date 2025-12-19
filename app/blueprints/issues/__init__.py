from flask import Blueprint

issues_bp = Blueprint('issues', __name__, template_folder='../../templates/issues')

from app.blueprints.issues import routes
