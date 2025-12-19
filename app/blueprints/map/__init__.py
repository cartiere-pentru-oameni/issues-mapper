from flask import Blueprint

map_bp = Blueprint('map', __name__, template_folder='../../templates/map')

from app.blueprints.map import routes
