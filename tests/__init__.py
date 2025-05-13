from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_object('config.Config')
    
    # Override with test config if provided
    if config:
        app.config.update(config)
    
    db.init_app(app)
    
    with app.app_context():
        from app import routes
        return app