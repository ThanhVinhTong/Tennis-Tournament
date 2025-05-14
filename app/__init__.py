from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
socketio = SocketIO(cors_allowed_origins='*')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    @app.shell_context_processor
    def make_shell_context():
        
        from app.models import User, MatchResult, ShareResult, MatchCalendar
        return {
            'db': db,
            'User': User,
            'MatchResult': MatchResult,
            'ShareResult': ShareResult,
            'MatchCalendar': MatchCalendar
        }

    # Initialize Extension
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Registration Blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app


