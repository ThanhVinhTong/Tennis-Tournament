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
   source venv/bin/activate    # macOS/Linux
   # Windows PowerShell:
   # venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Application

1. **Set environment variable for Flask**
   ```bash
   export FLASK_APP=run.py        # macOS/Linux
   set FLASK_APP=run.py           # Windows PowerShell
   ```
2. **Run the Flask server**
   ```bash
   flask run
   ```
3. **Access the app** Open your browser and navigate to `http://127.0.0.1:5000/`.

## Project Structure

```
CITS5505-Group-60-project/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── routes.py         # URL routes (views)
│   ├── templates/        # HTML Jinja2 templates
│   └── static/           # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── images/
├── run.py                # Application entry point
├── requirements.txt      # Python package dependencies
└── README.md             # Project documentation
```

## Running Tests
