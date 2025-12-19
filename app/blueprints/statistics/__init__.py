from flask import Blueprint

statistics_bp = Blueprint('statistics', __name__, template_folder='../../templates/statistics')

from app.blueprints.statistics import routes
