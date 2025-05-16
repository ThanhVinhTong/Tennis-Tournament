import pytest
from app import create_app, db
from flask_login import current_user

@pytest.fixture
def app():
    """
    Creates a Flask application fixture for testing.
    
    This fixture:
    1. Sets up a test configuration with an in-memory SQLite database
    2. Creates a new application instance with test settings
    3. Creates all database tables before each test
    4. Cleans up by removing the session and dropping tables after each test
    
    Returns:
        Flask application instance configured for testing
    """
    # Define test-specific configuration
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test'

    app = create_app(TestConfig)

    # Create application context and set up/tear down database
    with app.app_context():
        db.create_all()  # Create all database tables
        yield app        # Return app instance for testing
        db.session.remove()  # Clean up database session
        db.drop_all()    # Remove all tables after test

@pytest.fixture
def client(app):
    """
    Creates a test client fixture for the Flask application.
    
    Args:
        app: The Flask application fixture
    
    Returns:
        Flask test client that can be used to simulate HTTP requests
    """
    return app.test_client()

def test_app_creation(app):
    """
    Tests that the Flask application is properly created and configured.
    
    Verifies:
    1. Application instance exists
    2. Testing mode is properly enabled
    """
    assert app is not None
    assert app.config['TESTING'] is True

def test_home_page_route(client):
    """
    Tests the accessibility of the application's home page route.
    
    Verifies:
    1. Route responds with either:
       - 200 (OK) for successful access
       - 302 (Redirect) if login is required
    """
    response = client.get('/')
    assert response.status_code in [200, 302]  # 302 if login is required