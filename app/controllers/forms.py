from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms import TextAreaField, DateTimeField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    is_admin = BooleanField('Login as Admin')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(message='Invalid email address.')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), 
                                                 EqualTo('password', message='Please make sure your passwords match.')])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth (YYYY-MM-DD)', format='%Y-%m-%d')
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError('Email address is already registered.')

# Add new form classes for Subject, Chapter, Quiz, and Question
class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save Subject')

class ChapterForm(FlaskForm):
    name = StringField('Chapter Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    date_of_quiz = DateField('Quiz Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    time_duration = StringField('Time Duration (HH:MM)', 
                               validators=[DataRequired(), 
                                          Regexp('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', 
                                                message='Time must be in HH:MM format')])
    remarks = TextAreaField('Remarks')
    submit = SubmitField('Save Quiz')

class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = RadioField('Correct Answer', 
                              choices=[('option1', 'Option 1'), 
                                      ('option2', 'Option 2'),
                                      ('option3', 'Option 3'),
                                      ('option4', 'Option 4')],
                              validators=[DataRequired()])
    submit = SubmitField('Save Question')
