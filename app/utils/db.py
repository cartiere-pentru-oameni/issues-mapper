from supabase import create_client, Client
from flask import current_app, g


def get_db():
    """Get Supabase client from flask g object, create if not exists"""
    if 'db' not in g:
        g.db = create_client(
            current_app.config['SUPABASE_URL'],
            current_app.config['SUPABASE_SERVICE_KEY']
        )
    return g.db


def close_db(e=None):
    """Close database connection"""
    g.pop('db', None)


def init_app(app):
    """Initialize database utilities with Flask app"""
    app.teardown_appcontext(close_db)
