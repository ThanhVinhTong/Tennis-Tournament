from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, IntegerField, HiddenField, SubmitField, FileField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
import datetime


class PlayerForm(FlaskForm):
    name    = StringField('Player Name', validators=[DataRequired()])
    country = StringField('Country', validators=[Optional()])
    submit  = SubmitField('Add Player')
    
class MatchResultForm(FlaskForm):
    tournament_name = StringField('Competition Name', validators=[DataRequired()])
    player1         = SelectField('Player 1', coerce=int, validators=[DataRequired()])
    player2         = SelectField('Player 2', coerce=int, validators=[DataRequired()])
    score1          = IntegerField('Player 1 Score', validators=[DataRequired(), NumberRange(min=0)])
    score2          = IntegerField('Player 2 Score', validators=[DataRequired(), NumberRange(min=0)])
    winner          = HiddenField()  
    match_date      = DateField(
                         'Match Date (YYYY-MM-DD)',
                         format='%Y-%m-%d',
                         validators=[Optional()]
                      )
    submit_manual   = SubmitField('Submit Single')

    def validate_match_date(self, field):
        if field.data and field.data > datetime.date.today():
            raise ValidationError('Match date cannot be in the future.')

class UploadForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[
        FileRequired(message='Please select a CSV file'),
        FileAllowed(['csv'], 'Only CSV format is allowed')
    ])
    submit_csv = SubmitField('Upload CSV')

class ShareForm(FlaskForm):
    submit_share = SubmitField('Share Selected Result')
    




class UploadPlayersForm(FlaskForm):
    csv_file   = FileField('Player CSV File', validators=[
        FileRequired(message='Please select a CSV file'),
        FileAllowed(['csv'], 'Only CSV files allowed!')
    ])
    submit_csv = SubmitField('Upload Players CSV')

