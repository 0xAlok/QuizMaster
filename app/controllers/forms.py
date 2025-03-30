from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms import TextAreaField, RadioField, IntegerField # Import IntegerField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Regexp,
    NumberRange # Import NumberRange
)
from app.models.user import User


class LoginForm(FlaskForm):
    """Form for user and admin login."""

    username = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    is_admin = BooleanField("Login as Admin")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    """Form for new user registration."""

    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(message="Invalid email address.")],
    )
    full_name = StringField(
        "Full Name", validators=[DataRequired(), Length(min=2, max=100)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Please make sure your passwords match."),
        ],
    )
    qualification = StringField("Qualification")
    dob = DateField("Date of Birth (YYYY-MM-DD)", format="%Y-%m-%d")
    submit = SubmitField("Register")

    def validate_email(self, email):
        """Checks if the provided email (used as username) is already registered."""
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError(
                "That email address is already registered. Please use a different one or login."
            )


# --- Forms for Admin Management ---


class SubjectForm(FlaskForm):
    """Form for adding/editing subjects."""

    name = StringField(
        "Subject Name", validators=[DataRequired(), Length(min=2, max=100)]
    )
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save Subject")


class ChapterForm(FlaskForm):
    """Form for adding/editing chapters."""

    name = StringField(
        "Chapter Name", validators=[DataRequired(), Length(min=2, max=100)]
    )
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save Chapter")


class QuizForm(FlaskForm):
    """Form for adding/editing quizzes."""

    date_of_quiz = DateField(
        "Quiz Date (YYYY-MM-DD)", format="%Y-%m-%d", validators=[DataRequired()]
    )
    # Changed to IntegerField for total minutes
    time_duration = IntegerField(
        "Time Duration (Minutes)",
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Duration must be at least 1 minute.")
        ]
    )
    remarks = TextAreaField("Remarks")
    submit = SubmitField("Save Quiz")


class QuestionForm(FlaskForm):
    """Form for adding/editing questions."""

    question_text = TextAreaField("Question Text", validators=[DataRequired()])
    option1 = StringField("Option 1", validators=[DataRequired()])
    option2 = StringField("Option 2", validators=[DataRequired()])
    option3 = StringField("Option 3", validators=[DataRequired()])
    option4 = StringField("Option 4", validators=[DataRequired()])
    correct_option = RadioField(
        "Correct Answer",
        choices=[
            ("option1", "Option 1"),
            ("option2", "Option 2"),
            ("option3", "Option 3"),
            ("option4", "Option 4"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Question")
