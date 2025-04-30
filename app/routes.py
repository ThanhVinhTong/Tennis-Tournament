
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/visualise')
def visualise():
    return render_template('visualise.html')

@main_bp.route('/share')
def share():
    return render_template('share.html')

@main_bp.route('/upload')
def upload():
    return render_template('upload.html')


