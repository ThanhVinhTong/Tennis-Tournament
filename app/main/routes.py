from flask import (
    render_template, redirect, url_for, flash,
    request, jsonify
)
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc
from collections import defaultdict
import statistics




from app import db
from app.main import bp
from app.models import Player, MatchResult, ShareResult, User, MatchCalendar
from app.main import bp
from app.main.forms import PlayerForm, MatchResultForm, UploadForm
import csv, io, json, logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/home')
def home():
    """
    Introductory landing page, public.
    """
    return render_template('main/home.html', is_authenticated=current_user.is_authenticated)


@bp.route('/')
def index():
    """
    Root: if logged in, go to home; otherwise to login.
    """
    if current_user.is_authenticated:
        return render_template('main/home.html', is_authenticated=True)
    return redirect(url_for('auth.login'))

@bp.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        if not all([year, month is not None]):
            return jsonify({'error': 'Year and month are required'}), 400

        if current_user.is_authenticated:
            # Fetch matches for the logged-in user for the specified year and month
            matches = MatchCalendar.query.filter(
                MatchCalendar.user_id == current_user.id,
                func.extract('month', MatchCalendar.match_date) == month,
                func.extract('year', MatchCalendar.match_date) == year
            ).all()
            matches_by_day = {str(match.match_date.day): match.to_dict() for match in matches}  # Ensure string keys
        else:
            # Return empty matches for public access
            matches_by_day = {}

        return jsonify(matches_by_day), 200

    except Exception as e:
        logger.error(f"Error fetching matches: {str(e)}")
        return jsonify({'error': f'Failed to fetch matches: {str(e)}'}), 500

@bp.route('/api/matches', methods=['POST'])
@login_required
def add_match():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        title = data.get('title')
        players = data.get('players')
        time = data.get('time')
        court = data.get('court')
        match_date_str = data.get('match_date')
        month = data.get('month')

        # Log the received data
        logger.info(f"Received match data from user {current_user.id}: title={title}, players={players}, time={time}, court={court}, match_date={match_date_str}, month={month}")

        # Validate inputs
        if not all([title, players, time, match_date_str, month]):
            return jsonify({'error': 'All fields are required'}), 400

        try:
            month = int(month)
            if not (1 <= month <= 12):
                return jsonify({'error': 'Month must be between 1 and 12'}), 400
        except (TypeError, ValueError):
            return jsonify({'error': 'Month must be a valid integer'}), 400

        # Validate time format (HH:MM)
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            return jsonify({'error': 'Time must be in HH:MM format (e.g., 14:00)'}), 400

        # Parse match date
        try:
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

        # Check for duplicate matches for this user
        existing_match = MatchCalendar.query.filter_by(
            user_id=current_user.id,
            match_date=match_date,
            time=time,
            court=court
        ).first()

        if existing_match:
            return jsonify({'error': 'A match already exists at this date, time, and court for this user'}), 400
        else:
            # Set default court if empty or invalid
            court = court.strip() if court else 'Court 1'

            # Create new match
            new_match = MatchCalendar(
                title=title,
                players=players,
                time=time,
                court=court,
                match_date=match_date,
                month=month + 1,  # Convert to 1-based for storage
                user_id=current_user.id
            )

            flash(f"New match created: {new_match}")

            db.session.add(new_match)
            db.session.commit()

            # Log successful storage
            logger.info(f"Match stored successfully: ID={new_match.id} for user {current_user.id}")

            return jsonify({
                'message': 'Match added successfully',
                'match': new_match.to_dict()
            }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding match for user {current_user.id}: {str(e)}")
        return jsonify({'error': f'Failed to add match: {str(e)}'}), 500

# —— Player Management —— #
@bp.route('/players', methods=['GET', 'POST'])
@login_required
def manage_players():
    form = PlayerForm()
    players = Player.query.order_by(Player.name).all()

    if form.validate_on_submit():
        # Avoid duplicate names
        if Player.query.filter_by(name=form.name.data).first():
            flash('Player already exists.', 'warning')
        else:
            p = Player(name=form.name.data, country=form.country.data)
            db.session.add(p)
            db.session.commit()
            flash('✅ Player added.', 'success')
        return redirect(url_for('main.manage_players'))

    return render_template('main/players.html', form=form, players=players)

@bp.route('/players/delete/<int:pid>', methods=['POST'])
@login_required
def delete_player(pid):
    p = Player.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('🗑️ Player deleted.', 'info')
    return redirect(url_for('main.manage_players'))


# —— upload part —— #
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    manual_form = MatchResultForm(prefix='m')
    upload_form = UploadForm(prefix='u')

    # Load players into the form
    players = Player.query.order_by(Player.name).all()
    choices = [(p.id, p.name) for p in players]
    manual_form.player1.choices = choices
    manual_form.player2.choices = choices

    # —— 1. CSV upload & preview —— 
    if upload_form.validate_on_submit() and upload_form.submit_csv.data:
        data = upload_form.csv_file.data.read().decode('utf-8')
        stream = io.StringIO(data)
        reader = csv.DictReader(stream)

        rows, errors = [], []
        for idx, row in enumerate(reader, start=1):
            missing = [k for k,v in row.items() if not v or not v.strip()]
            if missing:
                errors.append((idx, missing))
            rows.append(row)

        return render_template(
            'main/preview_upload.html',
            rows=rows,
            rows_json=json.dumps(rows),
            errors=errors
        )

    # —— 2. Manual entry —— 
    if manual_form.submit_manual.data and manual_form.validate_on_submit():
        p1_id = manual_form.player1.data
        p2_id = manual_form.player2.data
        s1 = manual_form.score1.data
        s2 = manual_form.score2.data

        if s1 == s2:
            flash('⚠️ There is no tied game in Tennis.', 'danger')
            return redirect(url_for('main.upload'))

        winner_id = p1_id if s1 > s2 else p2_id
        score_str = f"{s1}-{s2}"

        m = MatchResult(
            tournament_name=manual_form.tournament_name.data,
            player1_id=p1_id,
            player2_id=p2_id,
            winner_id=winner_id,
            score=score_str,
            match_date=manual_form.match_date.data or datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(m)
        db.session.commit()
        flash('✅ Match recorded.', 'success')
        return redirect(url_for('main.view_stats'))

    # —— GET or validation failure —— 
    return render_template(
        'main/upload.html',
        manual_form=manual_form,
        upload_form=upload_form,
        today=date.today().isoformat()
    )


@bp.route('/upload/confirm', methods=['POST'])
@login_required
def upload_confirm():
    rows = json.loads(request.form.get('rows_json', '[]'))
    if request.form.get('action') == 'selected':
        idxs = request.form.getlist('selected')
        rows = [rows[int(i)] for i in idxs]

    count = 0
    for r in rows:
        # Lookup players by name
        p1 = Player.query.filter_by(name=r['player1']).first()
        p2 = Player.query.filter_by(name=r['player2']).first()
        w  = Player.query.filter_by(name=r['winner']).first()
        if not (p1 and p2 and w):
            continue

        try:
            m = MatchResult(
                tournament_name=r['tournament_name'],
                match_date=datetime.strptime(r['match_date'], '%Y-%m-%d'),
                player1_id=p1.id,
                player2_id=p2.id,
                winner_id=w.id,
                score=r['score'],
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
    # 全库用户可见比赛（自己和私密分享）
    own = MatchResult.query.filter_by(user_id=current_user.id).all()
    shared = [sr.match_result for sr in ShareResult.query.filter_by(
        recipient_id=current_user.id, is_public=False).all()]
    matches = sorted(own + shared, key=lambda m: m.match_date)

    # KPI 1: 总比赛数
    total_matches = len(matches)

    # 月度比赛统计
    month_counts = {}
    for m in matches:
        key = m.match_date.strftime('%Y-%m')
        month_counts[key] = month_counts.get(key, 0) + 1
    busiest_month = max(month_counts, key=month_counts.get) if month_counts else ''
    avg_per_month = round(total_matches / len(month_counts), 1) if month_counts else 0

    # 玩家统计
    players = Player.query.all()
    player_names = [p.name for p in players]
    played_counts = []
    win_counts = []
    loss_counts = []
    win_pcts = []

    for p in players:
        played = db.session.query(func.count(MatchResult.id)).filter(
            (MatchResult.player1_id == p.id) | (MatchResult.player2_id == p.id)
        ).scalar() or 0
        wins = db.session.query(func.count(MatchResult.id)).filter(
            MatchResult.winner_id == p.id
        ).scalar() or 0
        losses = played - wins
        pct = round((wins / played * 100), 1) if played else 0
        played_counts.append(played)
        win_counts.append(wins)
        loss_counts.append(losses)
        win_pcts.append(pct)

    # KPI 2 & 3: 胜率最高/最低
    if win_pcts:
        max_i = win_pcts.index(max(win_pcts))
        min_i = win_pcts.index(min(win_pcts))
        highest_win_player = player_names[max_i]
        highest_win_pct = win_pcts[max_i]
        lowest_win_player = player_names[min_i]
        lowest_win_pct = win_pcts[min_i]
    else:
        highest_win_player = lowest_win_player = ''
        highest_win_pct = lowest_win_pct = 0

    # 月度趋势折线
    monthly_labels = sorted(month_counts.keys())
    monthly_totals = [month_counts[m] for m in monthly_labels]
    # 回归趋势线计算
    n = len(monthly_totals)
    xs = list(range(n))
    ys = monthly_totals
    if n >= 2:
        xm = sum(xs) / n; ym = sum(ys) / n
        num = sum((x-xm)*(y-ym) for x,y in zip(xs,ys))
        den = sum((x-xm)**2 for x in xs)
        slope = num/den if den else 0
        intercept = ym - slope*xm
        trend = [round(slope*x + intercept,1) for x in xs]
    else:
        trend = monthly_totals

    # 饼图：胜场占比
    pie_labels = player_names
    pie_data = win_counts

    # 胜场排行榜
    leaderboard = sorted(
        [{'player': player_names[i], 'wins': win_counts[i]} for i in range(len(player_names))],
        key=lambda x: x['wins'], reverse=True
    )

    return render_template('main/view_stats.html',
        # KPI
        total_matches=total_matches,
        busiest_month=busiest_month,
        avg_per_month=avg_per_month,
        highest_win_player=highest_win_player,
        highest_win_pct=highest_win_pct,
        lowest_win_player=lowest_win_player,
        lowest_win_pct=lowest_win_pct,
        # Player stats
        player_names=player_names,
        played_counts=played_counts,
        win_counts=win_counts,
        loss_counts=loss_counts,
        # Monthly trend
        monthly_labels=monthly_labels,
        monthly_totals=monthly_totals,
        trend=trend,
        # Pie
        pie_labels=pie_labels,
        pie_data=pie_data,
        # Leaderboard
        leaderboard=leaderboard
    )

    
    
    
    
    
# —— received_results part —— #
@bp.route('/received_results')
@login_required
def received_results():
    private_ids = (
        db.session.query(ShareResult.match_result_id)
        .filter(ShareResult.recipient_id == current_user.id, ShareResult.is_public == False)
        .subquery()
    )
    private_matches = (
        MatchResult.query
        .filter(MatchResult.id.in_(private_ids))
        .order_by(MatchResult.match_date.desc())
        .all()
    )

    return render_template(
        'main/received_results.html',
        private_matches=private_matches
    )


# —— API endpoints —— #
@bp.route('/api/users')
@login_required
def api_users():
    users = User.query.with_entities(User.username).order_by(User.username).all()
    return jsonify([u[0] for u in users])


@bp.route('/api/match_dates')
@login_required
def api_match_dates():
    dates = (
        db.session.query(func.date(MatchResult.match_date))
                  .filter_by(user_id=current_user.id)
                  .distinct()
                  .order_by(desc(MatchResult.match_date))
                  .all()
    )
    return jsonify([d[0].strftime('%Y-%m-%d') for d in dates])


@bp.route('/api/matches_by_date')
@login_required
def api_matches_by_date():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify([])
    dt = datetime.strptime(date_str, '%Y-%m-%d').date()
    matches = (MatchResult.query
               .filter_by(user_id=current_user.id)
               .filter(func.date(MatchResult.match_date) == dt)
               .order_by(desc(MatchResult.match_date))
               .all())
    return jsonify([
        {'id': m.id, 'title': f'{m.player1} vs {m.player2} ({m.score})'}
        for m in matches
    ])


# —— share part —— #
@bp.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    if request.method == 'GET':
        # 1. Current user's games
        raw_matches = (
            MatchResult.query
                       .filter_by(user_id=current_user.id)
                       .order_by(desc(MatchResult.match_date))
                       .all()
        )
        # Preprocessing: Convert each MatchResult into a dictionary with player1_name, player2_name, winner_name
        share_matches = []
        for m in raw_matches:
            p1 = Player.query.get(m.player1_id)
            p2 = Player.query.get(m.player2_id)
            w  = Player.query.get(m.winner_id)
            share_matches.append({
                'id':         m.id,
                'date':       m.match_date.strftime('%Y-%m-%d'),
                'tournament': m.tournament_name,
                'players':    f"{p1.name if p1 else '-'} vs {p2.name if p2 else '-'}",
                'score':      m.score,
                'winner':     w.name if w else '-'
            })

        # 2. Pull down the list of available users
        all_users = User.query.filter(User.id != current_user.id) \
                              .order_by(User.username).all()
        all_users_data = [{'id': u.id, 'username': u.username} for u in all_users]

        # 3. Private shared mapping
        shared_map = defaultdict(list)
        for sr in ShareResult.query.filter_by(sender_id=current_user.id, is_public=False):
            shared_map[sr.match_result_id].append(sr.recipient_id)

        # 4. Private sharing history
        share_history = []
        recs = (
            ShareResult.query
                       .filter_by(sender_id=current_user.id, is_public=False)
                       .order_by(desc(ShareResult.timestamp))
                       .all()
        )
        for sr in recs:
            mr = sr.match_result
            p1 = Player.query.get(mr.player1_id)
            p2 = Player.query.get(mr.player2_id)
            share_history.append({
                'date':       sr.timestamp.strftime('%Y-%m-%d'),
                'tournament': mr.tournament_name,
                'players':    f"{p1.name if p1 else '-'} vs {p2.name if p2 else '-'}",
                'recipient':  sr.recipient.username
            })

        return render_template(
            'main/share.html',
            share_matches=share_matches,
            all_users_data=all_users_data,
            shared_map=shared_map,
            current_username=current_user.username,
            share_history=share_history
        )

    # POST: Private sharing
    data = request.get_json() or {}
    match_ids = data.get('match_ids', [])
    usernames = data.get('usernames', [])
    if not match_ids or not usernames:
        return jsonify({'message': 'match_ids and usernames required'}), 400

    for mid in match_ids:
        for uname in usernames:
            user = User.query.filter_by(username=uname).first()
            if not user or user.id == current_user.id:
                continue
            exists = ShareResult.query.filter_by(
                match_result_id=mid,
                sender_id=current_user.id,
                recipient_id=user.id,
                is_public=False
            ).first()
            if not exists:
                db.session.add(ShareResult(
                    match_result_id=mid,
                    sender_id=current_user.id,
                    recipient_id=user.id,
                    is_public=False,
                    timestamp=datetime.utcnow()
                ))
    db.session.commit()
    return jsonify({'result': 'shared_private'}), 200

@bp.route('/unshare/<int:share_id>', methods=['POST'])
@login_required
def unshare(share_id):
    sr = ShareResult.query.get_or_404(share_id)
    if sr.sender_id != current_user.id:
        abort(403)

    db.session.delete(sr)
    db.session.commit()
    flash('Share record removed.', 'info')
    return redirect(url_for('main.share'))
