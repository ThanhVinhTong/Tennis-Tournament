from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        #login_user(user, remember=form.remember_me.data)
        login_user(user)
        flash('Login successful', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        # 1. Do format validation first (including Email() validator)
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                country=form.country.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
                flash('Registration successful. You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            except IntegrityError:
                db.session.rollback()
                flash('This email is already registered or invalid. Please use another email.', 'danger')
            except Exception:
                db.session.rollback()
                flash('Registration failed due to server error. Please try again later.', 'danger')
        else:
            # 2. If format validation fails, collect and flash the error of each field
            for field, errors in form.errors.items():
                label = getattr(form, field).label.text
                for error in errors:
                    flash(f"{label}: {error}", 'danger')
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Exit Success', 'info')
    return redirect(url_for('auth.login'))
