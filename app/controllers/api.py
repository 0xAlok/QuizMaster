from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.user import User

api_bp = Blueprint("api", __name__, url_prefix="/api")

# --- Subject Endpoints ---

@api_bp.route("/subjects", methods=["GET"])
def get_subjects():
    """Returns a list of all subjects, ordered by name."""
    subjects = Subject.query.order_by(Subject.name).all()
    subjects_list = [
        {"id": s.id, "name": s.name, "description": s.description} for s in subjects
    ]
    return jsonify(subjects_list)


@api_bp.route("/subjects/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    """Returns details for a specific subject by its ID."""
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(
        {"id": subject.id, "name": subject.name, "description": subject.description}
    )

# --- Chapter Endpoints ---

@api_bp.route("/subjects/<int:subject_id>/chapters", methods=["GET"])
def get_chapters_for_subject(subject_id):
    """Returns a list of chapters for a given subject ID, ordered by name."""
    chapters = (
        Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.name).all()
    )
    chapters_list = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "subject_id": c.subject_id,
        }
        for c in chapters
    ]
    return jsonify(chapters_list)


@api_bp.route("/chapters/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):
    """Returns details for a specific chapter by its ID."""
    chapter = Chapter.query.get_or_404(chapter_id)
    return jsonify(
        {
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "subject_id": chapter.subject_id,
        }
    )

# --- Quiz Endpoints ---

@api_bp.route("/chapters/<int:chapter_id>/quizzes", methods=["GET"])
def get_quizzes_for_chapter(chapter_id):
    """Returns a list of quizzes for a given chapter ID, ordered by date."""
    quizzes = (
        Quiz.query.filter_by(chapter_id=chapter_id)
        .order_by(Quiz.date_of_quiz.desc())
        .all()
    )
    quizzes_list = [
        {
            "id": q.id,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.isoformat(),
            "time_duration_minutes": q.time_duration,
            "remarks": q.remarks,
        }
        for q in quizzes
    ]
    return jsonify(quizzes_list)

@api_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    """Returns details for a specific quiz by its ID."""
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify(
        {
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "date_of_quiz": quiz.date_of_quiz.isoformat(),
            "time_duration_minutes": quiz.time_duration,
            "remarks": quiz.remarks,
        }
    )

# --- Question Endpoints ---

@api_bp.route("/quizzes/<int:quiz_id>/questions", methods=["GET"])
def get_questions_for_quiz(quiz_id):
    """
    Returns a list of questions for a given quiz ID (excluding answers),
    ordered by question ID.
    """
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.id).all()
    questions_list = [
        {
            "id": q.id,
            "quiz_id": q.quiz_id,
            "question_text": q.question_text,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
        }
        for q in questions
    ]
    return jsonify(questions_list)

# --- Score Endpoints ---

@api_bp.route("/scores", methods=["GET"])
@login_required
def get_user_scores():
    """
    Returns a list of scores for the currently logged-in user,
    ordered by most recent attempt first. Requires user login.
    """
    if not isinstance(current_user, User):
        return jsonify(
            {"error": "Access denied. This endpoint is for users only."}
        ), 403

    scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(Score.time_stamp_of_attempt.desc())
        .all()
    )
    scores_list = [
        {
            "id": s.id,
            "quiz_id": s.quiz_id,
            "user_id": s.user_id,
            "score_percentage": s.total_scored,
            "timestamp": s.time_stamp_of_attempt.isoformat(),
        }
        for s in scores
    ]
    return jsonify(scores_list)
