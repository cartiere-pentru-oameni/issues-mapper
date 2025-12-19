from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database utilities
    from app.utils import db
    db.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.upload import upload_bp
    from app.blueprints.map import map_bp
    from app.blueprints.issues import issues_bp
    from app.blueprints.statistics import statistics_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(map_bp, url_prefix='/map')
    app.register_blueprint(issues_bp, url_prefix='/issues')
    app.register_blueprint(statistics_bp, url_prefix='/statistics')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    # Add logging for all requests
    @app.before_request
    def log_request():
        import logging
        from flask import request
        logging.info(f"Request: {request.method} {request.path}")

    return app
