import pytest
from app import create_app, db
from app.models import User, Player, MatchResult, ShareResult, MatchCalendar
from datetime import datetime

@pytest.fixture
def app():
    """
    Creates a Flask application fixture for testing models.
    
    This fixture:
    1. Sets up a test configuration with an in-memory SQLite database
    2. Creates all database tables in a fresh test environment
    3. Provides transaction rollback after each test
    4. Cleans up by removing the session and dropping tables
    
    Returns:
        Flask application instance configured for testing
    """
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-key'

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()  # Create all database tables
        yield app        # Return app instance for testing
        db.session.remove()  # Clean up database session
        db.drop_all()    # Remove all tables after test

@pytest.fixture
def session(app):
    """
    Creates a database session fixture for testing models.
    
    Args:
        app: The Flask application fixture
    
    Returns:
        SQLAlchemy session object for database operations
    """
    return db.session

def test_create_user(session):
    """
    Tests User model creation and password hashing functionality.
    
    Verifies:
    1. User creation with username and email
    2. Password hashing and verification
    3. Correct string representation of User object
    
    Args:
        session: SQLAlchemy session fixture
    """
    user = User(username='testuser', email='test@example.com')
    user.set_password('secret')
    session.add(user)
    session.commit()

    assert user.check_password('secret') is True
    assert user.check_password('wrong') is False
    assert repr(user) == '<User testuser>'

def test_create_player(session):
    """
    Tests Player model creation and basic functionality.
    
    Verifies:
    1. Player creation with name and country
    2. Automatic ID assignment
    3. Correct string representation of Player object
    
    Args:
        session: SQLAlchemy session fixture
    """
    player = Player(name='Roger Federer', country='Switzerland')
    session.add(player)
    session.commit()

    assert player.id is not None
    assert repr(player) == '<Player Roger Federer>'

def test_match_calendar_to_dict(session):
    """
    Tests MatchCalendar model creation and dictionary conversion.
    
    Verifies:
    1. User creation for calendar ownership
    2. Match calendar entry creation with all fields
    3. Correct dictionary representation of calendar entry
    4. Date formatting and month extraction
    
    Args:
        session: SQLAlchemy session fixture
    """
    # Create a user for the calendar entry
    user = User(username='calendaruser', email='cal@example.com')
    user.set_password('abc')
    session.add(user)
    session.commit()

    # Create a match calendar entry
    match = MatchCalendar(
        title='Friendly Match',
        players='Nadal vs Djokovic',
        time='16:30',
        court='Court 1',
        match_date=datetime(2025, 5, 10),
        month=5,
        user_id=user.id
    )
    session.add(match)
    session.commit()

    # Test dictionary conversion and date handling
    d = match.to_dict()
    assert d['title'] == 'Friendly Match'
    assert d['month'] == 5
    assert match.get_month() == 5
    assert "2025-05-10" in d['match_date']
