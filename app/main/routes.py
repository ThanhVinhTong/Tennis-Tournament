# app/main/routes.py

from datetime import datetime
from sqlalchemy import func, desc
from flask import (
    render_template, redirect, url_for, flash,
    request, jsonify
)
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import datetime, date
from app import db
from app.models import MatchResult, ShareResult, User
from app.main import bp
from app.main.forms import MatchResultForm, UploadForm
import csv, io, json


@bp.route('/home')
def home():
    """
    Introductory landing page, public.
    """
    return render_template('main/home.html')




