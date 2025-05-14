from datetime import datetime, UTC

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Player(db.Model):
    __tablename__ = 'player'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(80), unique=True, nullable=False)
    country    = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Player {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    country       = db.Column(db.String(64), nullable=True)

    match_results  = db.relationship('MatchResult', backref='author', lazy='dynamic')
    shared_results = db.relationship(
        'ShareResult',
        foreign_keys='ShareResult.recipient_id',
        backref='recipient',
        lazy='dynamic'
    )
    sent_results   = db.relationship(
        'ShareResult',
        foreign_keys='ShareResult.sender_id',
        backref='sender',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class MatchResult(db.Model):
    __tablename__ = 'match_result'
    id              = db.Column(db.Integer, primary_key=True)
    tournament_name = db.Column(db.String(128), nullable=False)
    match_date      = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    winner_id  = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score    = db.Column(db.String(20), nullable=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (
            f'<MatchResult id={self.id} ' 
            f'{self.player1_id} vs {self.player2_id} ' 
            f'on {self.match_date.date()}>'
        )

class ShareResult(db.Model):
    __tablename__ = 'share_result'
    id               = db.Column(db.Integer, primary_key=True)
    match_result_id  = db.Column(db.Integer, db.ForeignKey('match_result.id'), nullable=False)
    sender_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_public        = db.Column(db.Boolean, default=False, nullable=False)
    timestamp        = db.Column(db.DateTime, default=datetime.utcnow)
    match_result = db.relationship('MatchResult', backref='shares')

    def __repr__(self):
        return (
            f'<ShareResult match {self.match_result_id} ' 
            f'from {self.sender_id} to {self.recipient_id} ' 
            f'public={self.is_public}>'
        )


class MatchCalendar(db.Model):
    """
    Model for storing scheduled tennis matches, private to each user
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    players = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(5), nullable=False)  # Format: "HH:MM"
    court = db.Column(db.String(50), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # Month of the match
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (f'<ShareResult match {self.match_result_id} '
                f'from {self.sender_id} to {self.recipient_id} '
                f'public={self.is_public}>')
    
class MatchCalendar(db.Model):
    """
    Model for storing scheduled tennis matches, private to each user
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    players = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(5), nullable=False)  # Format: "HH:MM"
    court = db.Column(db.String(50), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # Month of the match
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'players': self.players,
            'time': self.time,
            'court': self.court,
            'match_date': self.match_date.strftime('%Y-%m-%d'),
            'month': self.month,
            'user_id': self.user_id
        }
    
    def get_month(self):
        return self.month

