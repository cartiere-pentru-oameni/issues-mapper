from flask import Blueprint

upload_bp = Blueprint('upload', __name__, template_folder='../../templates/upload')

from app.blueprints.upload import routes
