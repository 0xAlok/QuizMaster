from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    jsonify,
)
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from sqlalchemy import func, or_

user_bp = Blueprint("user", __name__, url_prefix="/user")


def user_required(f):
    """Decorator to ensure the logged-in user is a regular User."""

    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, User):
            flash("This page is for regular users only", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# --- Helper functions for user dashboard data ---


def get_user_scores(user_id):
    """Fetches all scores for a given user, ordered by attempt time."""
    return (
        Score.query.filter_by(user_id=user_id)
        .order_by(Score.time_stamp_of_attempt.asc())
        .all()
    )


def get_upcoming_quizzes(limit=10):
    """Fetches upcoming quizzes from today onwards."""
    today = date.today()
    return (
        Quiz.query.filter(Quiz.date_of_quiz >= today)
        .order_by(Quiz.date_of_quiz.asc())
        .limit(limit)
        .all()
    )


def prepare_score_trend_data(scores):
    """Prepares labels and data for the score trend chart."""
    labels = [score.time_stamp_of_attempt.timestamp() * 1000 for score in scores]
    data = [score.total_scored for score in scores]
    return labels, data


def prepare_avg_score_per_subject_data(user_id):
    """Prepares labels and data for the average score per subject chart."""
    data = (
        db.session.query(Subject.name, func.avg(Score.total_scored))
        .select_from(Score)
        .join(Quiz, Score.quiz_id == Quiz.id)
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Score.user_id == user_id)
        .group_by(Subject.name)
        .order_by(Subject.name)
        .all()
    )
    labels = [item[0] for item in data]
    averages = [round(item[1], 1) if item[1] is not None else 0 for item in data]
    return labels, averages


def prepare_attempts_per_subject_data(user_id):
    """Prepares labels and data for the attempts per subject chart."""
    data = (
        db.session.query(Subject.name, func.count(Score.id))
        .select_from(Score)
        .join(Quiz, Score.quiz_id == Quiz.id)
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Score.user_id == user_id)
        .group_by(Subject.name)
        .order_by(Subject.name)
        .all()
    )
    labels = [item[0] for item in data]
    counts = [item[1] for item in data]
    return labels, counts


def calculate_overall_stats(scores):
    """Calculates total attempts and average score from a list of scores."""
    total_attempts = len(scores)
    average_score = 0
    if total_attempts > 0:
        valid_scores = [
            s.total_scored for s in scores if isinstance(s.total_scored, (int, float))
        ]
        if valid_scores:
            average_score = sum(valid_scores) / len(valid_scores)
    return total_attempts, average_score


# --- User Routes ---


@user_bp.route("/dashboard")
@user_required
def dashboard():
    """Displays the user dashboard with subjects, stats, and charts."""
    user_id = current_user.id

    subjects = Subject.query.all()
    user_scores = get_user_scores(user_id)
    upcoming_quizzes = get_upcoming_quizzes()

    total_attempts, average_score = calculate_overall_stats(user_scores)

    score_labels, score_data = prepare_score_trend_data(user_scores)
    avg_score_subject_labels, avg_score_subject_data = (
        prepare_avg_score_per_subject_data(user_id)
    )
    attempt_subject_labels, attempt_subject_data = prepare_attempts_per_subject_data(
        user_id
    )

    context = {
        "subjects": subjects,
        "scores": user_scores,
        "upcoming_quizzes": upcoming_quizzes,
        "total_attempts": total_attempts,
        "average_score": average_score,
        "score_labels": score_labels,
        "score_data": score_data,
        "avg_score_subject_labels": avg_score_subject_labels,
        "avg_score_subject_data": avg_score_subject_data,
        "attempt_subject_labels": attempt_subject_labels,
        "attempt_subject_data": attempt_subject_data,
    }

    return render_template("user/dashboard.html", **context)


@user_bp.route("/subjects")
@user_required
def subjects():
    """Displays a list of subjects with search functionality."""
    search_term = request.args.get("search", "")
    query = Subject.query

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Subject.name.ilike(search_pattern),
                Subject.description.ilike(search_pattern),
            )
        )

    subjects = query.order_by(Subject.name).all()
    return render_template(
        "user/subjects.html", subjects=subjects, search_term=search_term
    )


@user_bp.route("/subject/<int:subject_id>/chapters")
@user_required
def chapters(subject_id):
    """Displays chapters for a specific subject."""
    subject = Subject.query.get_or_404(subject_id)
    chapters = (
        Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.name).all()
    )
    return render_template("user/chapters.html", subject=subject, chapters=chapters)


@user_bp.route("/chapter/<int:chapter_id>/quizzes")
@user_required
def quizzes(chapter_id):
    """Displays quizzes for a specific chapter with search."""
    chapter = Chapter.query.get_or_404(chapter_id)
    search_term = request.args.get("search", "")
    query = Quiz.query.filter_by(chapter_id=chapter_id)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Quiz.remarks.ilike(search_pattern))

    quizzes = query.order_by(Quiz.date_of_quiz.desc()).all()
    today = datetime.now().date()
    return render_template(
        "user/quizzes.html",
        chapter=chapter,
        quizzes=quizzes,
        today=today,
        search_term=search_term,
    )


@user_bp.route("/quiz/<int:quiz_id>/start")
@user_required
def start_quiz(quiz_id):
    """Displays the quiz start page with instructions."""
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.date_of_quiz != datetime.now().date():
        flash("This quiz is not available today.", "danger")
        return redirect(url_for("user.quizzes", chapter_id=quiz.chapter_id))

    previous_attempt = Score.query.filter_by(
        user_id=current_user.id, quiz_id=quiz_id
    ).first()
    return render_template(
        "user/start_quiz.html", quiz=quiz, previous_attempt=previous_attempt
    )


@user_bp.route("/quiz/<int:quiz_id>/attempt")
@user_required
def attempt_quiz(quiz_id):
    """Displays the quiz attempt interface and starts the timer."""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.id).all()

    if not questions:
        flash("This quiz has no questions.", "warning")
        return redirect(url_for("user.start_quiz", quiz_id=quiz_id))

    # Set up quiz timer in session
    session["quiz_start_time"] = datetime.now().timestamp()
    session["quiz_end_time"] = session["quiz_start_time"] + (quiz.time_duration * 60)

    return render_template("user/attempt_quiz.html", quiz=quiz, questions=questions)


# --- Helper function for quiz submission ---


def calculate_quiz_results(questions, form_data):
    """Calculates the score and detailed results from submitted quiz answers."""
    total_questions = len(questions)
    correct_answers = 0
    results_details = {}

    for question in questions:
        question_id_str = str(question.id)
        form_field_name = f"question_{question_id_str}"
        selected_answer_str = form_data.get(form_field_name)

        selected_answer_int = None
        is_correct = False

        if selected_answer_str:
            try:
                selected_answer_int = int(selected_answer_str)
                if selected_answer_int == question.correct_answer:
                    is_correct = True
                    correct_answers += 1
            except ValueError:
                pass

        results_details[question_id_str] = {
            "selected": selected_answer_int,
            "correct": question.correct_answer,
            "is_correct": is_correct,
        }

    score_percentage = 0
    if total_questions > 0:
        score_percentage = (correct_answers / total_questions) * 100

    return correct_answers, total_questions, score_percentage, results_details


@user_bp.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
@user_required
def submit_quiz(quiz_id):
    """Handles the submission of a quiz attempt."""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    correct_answers, total_questions, score_percentage, results_details = (
        calculate_quiz_results(questions, request.form)
    )

    try:
        new_score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            total_scored=score_percentage,
            time_stamp_of_attempt=datetime.now(),
        )
        db.session.add(new_score)
        db.session.commit()
        flash("Quiz submitted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving score: {e}", "danger")
        return redirect(url_for("user.dashboard"))

    session.pop("quiz_start_time", None)
    session.pop("quiz_end_time", None)

    return render_template(
        "user/quiz_result.html",
        quiz=quiz,
        questions=questions,
        results=results_details,
        score_percent=score_percentage,
        score_object=new_score,
        correct_answers=correct_answers,
        total_questions=total_questions,
    )


@user_bp.route("/quiz/check-time")
@user_required
def check_quiz_time():
    """AJAX endpoint to check remaining quiz time."""
    if "quiz_end_time" not in session:
        return jsonify({"time_remaining": 0, "expired": True})

    current_time = datetime.now().timestamp()
    end_time = session["quiz_end_time"]
    remaining = end_time - current_time

    return jsonify(
        {"time_remaining": max(0, int(remaining)), "expired": remaining <= 0}
    )


# --- Helper functions for history filtering ---


def apply_text_filter(query, search_term):
    """Applies text search filter to the history query."""
    if search_term:
        search_pattern = f"%{search_term}%"
        query = (
            query.join(Quiz)
            .join(Chapter)
            .join(Subject)
            .filter(
                or_(
                    Subject.name.ilike(search_pattern),
                    Chapter.name.ilike(search_pattern),
                )
            )
        )
    return query


def apply_score_filter(query, min_score, max_score):
    """Applies score range filter to the history query."""
    if min_score is not None:
        query = query.filter(Score.total_scored >= min_score)
    if max_score is not None:
        query = query.filter(Score.total_scored <= max_score)
    return query


def apply_date_filter(query, start_date_str, end_date_str):
    """Applies date range filter to the history query."""
    start_date, end_date = None, None
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(
                Score.time_stamp_of_attempt
                >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(
                Score.time_stamp_of_attempt
                <= datetime.combine(end_date, datetime.max.time())
            )
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "warning")
        start_date_str = ""
        end_date_str = ""
    return query, start_date_str, end_date_str


@user_bp.route("/history")
@user_required
def history():
    """Shows user's quiz attempt history with filtering capabilities."""
    user_id = current_user.id

    search_term = request.args.get("search", "")
    min_score = request.args.get("min_score", type=float)
    max_score = request.args.get("max_score", type=float)
    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")

    query = Score.query.filter_by(user_id=user_id)

    query = apply_text_filter(query, search_term)
    query = apply_score_filter(query, min_score, max_score)
    query, start_date_str, end_date_str = apply_date_filter(
        query, start_date_str, end_date_str
    )

    filtered_scores = query.order_by(Score.time_stamp_of_attempt.desc()).all()

    total_filtered_score = 0
    average_filtered_score = 0
    if filtered_scores:
        valid_scores = [
            s.total_scored
            for s in filtered_scores
            if isinstance(s.total_scored, (int, float))
        ]
        if valid_scores:
            total_filtered_score = sum(valid_scores)
            average_filtered_score = total_filtered_score / len(valid_scores)

    context = {
        "scores": filtered_scores,
        "average_score": average_filtered_score,
        "search_term": search_term,
        "min_score": min_score,
        "max_score": max_score,
        "start_date": start_date_str,
        "end_date": end_date_str,
    }

    return render_template("user/history.html", **context)
