import pytest
from app.main.forms import PlayerForm, MatchResultForm, UploadForm, ShareForm
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import MultiDict
import io
import datetime

# Needed for testing Flask-WTF forms
from flask import Flask
from flask_wtf.csrf import CSRFProtect

@pytest.fixture
def app():
    """
    Creates and configures a Flask test application.
    Returns a Flask app instance with CSRF protection disabled for testing.
    """
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.secret_key = 'test'
    CSRFProtect(app)
    return app

@pytest.fixture
def client(app):
    """
    Creates a test client for the Flask application.
    Returns a test client that can be used to simulate HTTP requests.
    """
    return app.test_client()

def test_player_form_valid(app):
    """
    Tests that the PlayerForm validates correctly with valid input data.
    Checks if form validates when proper name and country are provided.
    """
    with app.test_request_context():
        form = PlayerForm(name="Roger Federer", country="Switzerland")
        assert form.validate() is True

def test_player_form_missing_name(app):
    """
    Tests that the PlayerForm properly handles missing name field.
    Verifies that form validation fails when name is empty and appropriate error message is shown.
    """
    with app.test_request_context():
        form = PlayerForm(name="", country="India")
        assert form.validate() is False
        assert "This field is required." in form.name.errors[0]

def test_match_result_future_date_invalid(app):
    """
    Tests that the MatchResultForm rejects future dates.
    Verifies that form validation fails when match date is set to tomorrow
    and appropriate error message is displayed.
    """
    with app.test_request_context():
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        formdata = MultiDict({
            'tournament_name': 'Australian Open',
            'player1': '1',
            'player2': '2',
            'score1': '3',
            'score2': '2',
            'winner': '1',
            'match_date': tomorrow,
            'submit_manual': 'Submit Single'
        })

        form = MatchResultForm(formdata=formdata)
        form.player1.choices = [(1, 'Player 1')]
        form.player2.choices = [(2, 'Player 2')]

        is_valid = form.validate()
        print("Errors:", form.errors)

        assert is_valid is False
        assert "Match date cannot be in the future." in form.match_date.errors[0]

def test_upload_form_accepts_csv(app):
    """
    Tests that the UploadForm accepts valid CSV files.
    Creates a mock CSV file and verifies that form validation passes.
    """
    with app.test_request_context():
        file_data = FileStorage(
            stream=io.BytesIO(b"name,score\nplayer1,10"),
            filename="test.csv",
            content_type="text/csv"
        )
        form = UploadForm()
        form.csv_file.data = file_data
        assert form.validate() is True

def test_upload_form_rejects_non_csv(app):
    """
    Tests that the UploadForm rejects non-CSV files.
    Attempts to upload an HTML file and verifies that form validation fails
    with appropriate error message.
    """
    with app.test_request_context():
        file_data = FileStorage(
            stream=io.BytesIO(b"<html>not csv</html>"),
            filename="test.html",
            content_type="text/html"
        )
        form = UploadForm()
        form.csv_file.data = file_data
        assert form.validate() is False
        assert "Only CSV format is allowed" in form.csv_file.errors[0]

def test_share_form_exists(app):
    """
    Tests that the ShareForm exists and validates with default values.
    Verifies basic functionality of the share form.
    """
    with app.test_request_context():
        form = ShareForm()
        assert form.validate() is True
