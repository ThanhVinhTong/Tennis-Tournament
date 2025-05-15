import pytest
from app import create_app, db
from flask_login import current_user

@pytest.fixture
def app():
    # Use the testing configuration
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test'

    app = create_app(TestConfig)

    # Set up application context for the test
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True

def test_home_page_route(client):
    response = client.get('/')
    assert response.status_code in [200, 302]  # 302 if login is required