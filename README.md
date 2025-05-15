# CITS5505-Group-60-project

A Flask-based web application for tracking tennis tournaments, matches, and player data. Users can upload match data (single or CSV), view analytics, and selectively share results with other users.

## Project Description

This application provides four main views:

1. **Introductory**: Overview of the application and user login/register.
2. **Upload Data**: Upload a single match or a CSV file containing multiple match records.
3. **Visualise Data**: Interactive analytics dashboard showing match statistics and performance trends.
4. **Share Data**: Select matches or players to share with other users.

Built with:

* **Flask** (Python web framework)
* **SQLite** (via SQLAlchemy)
* **Bootstrap 5** (UI styling)
* **jQuery** (client-side scripting)

## Team Members

Student name: Zhenhao Zhu           Student ID: 24065267            Github: dynamicCat

Student name: Thanh Vinh Tong       Student ID: 22800814            Github: ThanhVinhTong

Student name: Mei Li                Student ID: 24212345            Github: meiliyuri

Student name: Aarthi Vadivel        Student ID: 24310357            Github: Aarthi2809

## Prerequisites

* Python 3.7 or higher
* Git
* Virtual environment tool: `venv` or `virtualenv`

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dynamicCat/CITS5505-Group-60-project.git
   cd CITS5505-Group-60-project
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   # MacOS/Linux:
   source venv/bin/activate
   # Windows PowerShell:
   venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Application


1. **Run the Flask server**

```bash
flask db upgrade
python run.py
```

2. **Access the app** Open your browser and navigate to `http://0.0.0.0:5001` (mac) / `http://127.0.0.1:5001`(windows)


## Reminder

### If you need to modify the model during development, be sure to run the following command in the virtual environment after the change:

```bash
flask db migrate -m "describe changes"
flask db upgrade
```

## Project Structure

```text
CITS5505-Group-60-project/
├── app/
│   ├── auth/      # Authentication blueprint (registration, login)
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── errors/    # Error handling blueprint (404, 500 pages)
│   │   ├── __init__.py
│   │   └── handlers.py
│   ├── main/      # Main function blueprint
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── static/            # Static Resources
│   │   ├── css/          # Stylesheets
│   │   ├── js/           # JavaScript files
│   │   └── images/       # Image assets
│   ├── templates/         # Jinja2 Templates
│   │   ├── auth/         # Authentication templates
│   │   ├── errors/       # Error page templates
│   │   └── main/         # Main feature templates
│   ├── __init__.py       # Application factory
│   └── models.py         # SQLAlchemy Models
│
├── tests/                 # Test suite
│   ├── conftest.py       # Test configuration
│   ├── test_auth.py      # Authentication tests
│   ├── test_models.py    # Model tests
│   └── test_routes.py    # Route tests
│
├── migrations/        # Flask-Migrate migration script
├── app.db             # SQLite database file
├── config.py          # Configuration
├── requirements.txt   # Python Dependencies
├── run.py             # Application entry
└── README.md

```

## Running Tests

The test suite consists of two main test files:

1. `test_forms.py` - Unit tests for form validation and processing:
   - Tests player registration form validation
   - Tests match result form date validation
   - Tests CSV file upload validation
   - Tests data sharing form functionality

2. `test_selenium.py` - End-to-end browser tests using Selenium:
   - Tests user registration and login flows
   - Tests responsive design across different viewports
   - Tests protected route redirects
   - Tests navigation menu functionality
   - Tests homepage elements

```bash
pytest tests/test_models.py
pytest tests/test_forms.py
pytest tests/test_selenium.py
```