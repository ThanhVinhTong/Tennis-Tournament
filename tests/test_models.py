import pytest
from app import create_app, db
from app.models import User, Player, MatchResult, ShareResult, MatchCalendar
from datetime import datetime

@pytest.fixture
def app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-key'

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    return db.session

def test_create_user(session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('secret')
    session.add(user)
    session.commit()

    assert user.check_password('secret') is True
    assert user.check_password('wrong') is False
    assert repr(user) == '<User testuser>'

def test_create_player(session):
    player = Player(name='Roger Federer', country='Switzerland')
    session.add(player)
    session.commit()

    assert player.id is not None
    assert repr(player) == '<Player Roger Federer>'

def test_match_calendar_to_dict(session):
    user = User(username='calendaruser', email='cal@example.com')
    user.set_password('abc')
    session.add(user)
    session.commit()

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

    d = match.to_dict()
    assert d['title'] == 'Friendly Match'
    assert d['month'] == 5
    assert match.get_month() == 5
    assert "2025-05-10" in d['match_date']
