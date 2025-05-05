
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

@bp.route('/')
def index():
    """
    Root: if logged in, go to input_result; otherwise to login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.upload'))
    return redirect(url_for('auth.login'))

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    manual_form = MatchResultForm(prefix='m')
    upload_form = UploadForm(prefix='u')


    users = User.query.order_by(User.username).all()
    choices = [(u.username, u.username) for u in users]
    manual_form.player1.choices = choices
    manual_form.player2.choices = choices

    # —— 1. Process CSV upload and preview ——
    if upload_form.validate_on_submit() and upload_form.submit_csv.data:
        # Read and parse CSV
        data = upload_form.csv_file.data.read().decode('utf-8')
        stream = io.StringIO(data)
        reader = csv.DictReader(stream)

        rows = []
        errors = []
        for idx, row in enumerate(reader, start=1):
            # Check for empty fields
            missing = [k for k, v in row.items() if not v or v.strip() == '']
            if missing:
                errors.append((idx, missing))
            rows.append(row)

        # Serialize and pass to the preview page
        rows_json = json.dumps(rows)
        return render_template(
            'main/preview_upload.html',
            rows=rows,
            rows_json=rows_json,
            errors=errors
        )

    # —— 2. Handle manual entry ——
    if manual_form.submit_manual.data and manual_form.validate_on_submit():
        p1 = manual_form.player1.data
        p2 = manual_form.player2.data
        s1 = manual_form.score1.data
        s2 = manual_form.score2.data

        if s1 == s2:
            flash('⚠️ Scores are tied; cannot determine a winner.', 'danger')
            return redirect(url_for('main.upload'))

        winner = p1 if s1 > s2 else p2
        score_str = f"{s1}-{s2}"

        m = MatchResult(
            tournament_name=manual_form.tournament_name.data,
            player1=p1,
            player2=p2,
            score=score_str,
            winner=winner,
            match_date=manual_form.match_date.data or datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(m)
        db.session.commit()
        flash('✅ Single record submitted successfully!', 'success')
        return redirect(url_for('main.view_stats'))


    # —— GET or verification failure ——
    return render_template(
        'main/upload.html',
        manual_form=manual_form,
        upload_form=upload_form,
        today=date.today().isoformat()
    )


@bp.route('/upload/confirm', methods=['POST'])
@login_required
def upload_confirm():
    rows = json.loads(request.form.get('rows_json','[]'))
    if request.form.get('action') == 'selected':
        idxs = request.form.getlist('selected')
        rows = [rows[int(i)] for i in idxs]
    count = 0
    for r in rows:
        try:
            m = MatchResult(
                tournament_name=r['tournament_name'],
                match_date=datetime.strptime(r['match_date'], '%Y-%m-%d'),
                player1=r['player1'],
                player2=r['player2'],
                score=r['score'],
                winner=r['winner'],
                user_id=current_user.id
            )
            db.session.add(m)
            count += 1
        except:
            continue
    db.session.commit()
    flash(f'✅ Successfully imported {count} records.', 'success')
    return redirect(url_for('main.view_stats'))













@bp.route('/view_stats')
@login_required
def view_stats():
    # —— 1. Personal (own + private sharing) ——
    own = (MatchResult.query
           .filter_by(user_id=current_user.id)
           .order_by(desc(MatchResult.match_date))
           .all())
    private_shared = [
        sr.match_result for sr in
        ShareResult.query
                   .filter_by(recipient_id=current_user.id, is_public=False)
                   .order_by(desc(ShareResult.timestamp))
                   .all()
    ]
    personal = sorted(own + private_shared,
                      key=lambda r: r.match_date, reverse=True)

    total = len(personal)
    wins  = sum(1 for r in personal if r.winner == current_user.username)
    losses = total - wins
    stats = {
        'total_matches':  total,
        'win_count':      wins,
        'win_percentage': f"{(wins/total*100):.1f}%" if total else "0.0%",
        'win_loss_ratio': f"{(wins/losses):.2f}" if losses else f"{wins:.2f}"
    }
    rev = list(reversed(personal))
    chart_labels = [r.match_date.strftime('%b %Y') for r in rev]
    chart_won    = [1 if r.winner == current_user.username else 0 for r in rev]
    chart_lost   = [1 if r.winner != current_user.username else 0 for r in rev]
    recent5      = personal[:5]

    # —— 2. Global public sharing statistics ——
    # Count the number of public shares by month (Bar Chart)
    monthly = (
        db.session.query(
            func.strftime('%Y-%m', MatchResult.match_date).label('month'),
            func.count(MatchResult.id).label('cnt')
        )
        .join(ShareResult, ShareResult.match_result_id == MatchResult.id)
        .filter(ShareResult.is_public == True)
        .group_by('month')
        .order_by('month')
        .all()
    )
    public_months = [m.month for m in monthly]
    public_counts = [m.cnt   for m in monthly]

    # Find the Top N popular winners (Bar & Pie)
    winners = (
        db.session.query(
            MatchResult.winner, func.count(MatchResult.id).label('cnt')
        )
        .join(ShareResult, ShareResult.match_result_id == MatchResult.id)
        .filter(ShareResult.is_public == True)
        .group_by(MatchResult.winner)
        .order_by(desc(func.count(MatchResult.id)))
        .limit(5)
        .all()
    )
    public_labels = [w.winner for w in winners]
    public_wins   = [w.cnt    for w in winners]

    # Trend of monthly wins of popular winners (Line Chart with regression exploration)
    # First take out all (month, winner, cnt) records
    monthly_wins_all = (
        db.session.query(
            func.strftime('%Y-%m', MatchResult.match_date).label('month'),
            MatchResult.winner,
            func.count(MatchResult.id).label('cnt')
        )
        .join(ShareResult, ShareResult.match_result_id == MatchResult.id)
        .filter(ShareResult.is_public == True,
                MatchResult.winner.in_(public_labels))
        .group_by('month', MatchResult.winner)
        .order_by('month')
        .all()
    )
    # Construct dictionary
    monthly_trends = {w: [0] * len(public_months) for w in public_labels}
    for rec in monthly_wins_all:
        month, winner, cnt = rec
        idx = public_months.index(month)
        monthly_trends[winner][idx] = cnt
    # —— 3. Site-wide user ranking ——
    user_win_counts = (
        db.session.query(MatchResult.winner, func.count(MatchResult.id).label('win_count'))
        .group_by(MatchResult.winner)
        .order_by(desc('win_count'))
        .all()
    )
    global_ranking = [{ 'username': u[0], 'win_count': u[1] } for u in user_win_counts]
    user_rank = next((i + 1 for i, u in enumerate(global_ranking) if u['username'] == current_user.username), None)
    

    return render_template(
        'main/view_stats.html',
        # Private Section
        stats=stats,
        chart_labels=chart_labels,
        chart_won=chart_won,
        chart_lost=chart_lost,
        recent_results=recent5,
        user_rank=user_rank,
        global_ranking=global_ranking,
        # Public part
        public_months=public_months,
        public_counts=public_counts,
        public_labels=public_labels,
        public_wins=public_wins,
        monthly_trends=monthly_trends
        
    )




