from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import Admin, User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.controllers.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to ensure the logged-in user is an Admin."""

    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash("You must be an admin to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Helper functions for dashboard data


def get_quiz_count_by_subject():
    """Fetches data for the 'Quizzes per Subject' chart."""
    data = (
        db.session.query(Subject.name, func.count(Quiz.id))
        .select_from(Subject)
        .outerjoin(Chapter, Subject.id == Chapter.subject_id)
        .outerjoin(Quiz, Chapter.id == Quiz.chapter_id)
        .group_by(Subject.name)
        .order_by(Subject.name)
        .all()
    )
    labels = [item[0] for item in data]
    counts = [item[1] for item in data]
    return labels, counts


def get_user_registration_trend():
    """Fetches data for the 'User Registration Trend' chart."""
    data = (
        db.session.query(
            func.DATE(User.created_at),
            func.count(User.id),
        )
        .select_from(User)
        .group_by(func.DATE(User.created_at))
        .order_by(func.DATE(User.created_at))
        .all()
    )
    labels = [
        datetime.strptime(item[0], "%Y-%m-%d").strftime("%Y-%m-%d")
        for item in data
        if item[0]
    ]
    counts = [item[1] for item in data if item[0]]
    return labels, counts


def get_average_score_by_quiz():
    """Fetches data for the 'Average Score per Quiz' chart."""
    data = (
        db.session.query(Quiz.id, func.avg(Score.total_scored))
        .select_from(Score)
        .join(Quiz, Score.quiz_id == Quiz.id)
        .group_by(Quiz.id)
        .order_by(Quiz.id)
        .all()
    )
    labels = [f"Quiz #{item[0]}" for item in data]
    averages = [round(item[1], 1) if item[1] is not None else 0 for item in data]
    return labels, averages


# --- Admin Routes ---


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Displays the admin dashboard with overview and statistics."""
    subjects_with_chapters = (
        Subject.query.options(joinedload(Subject.chapters)).order_by(Subject.name).all()
    )

    subject_labels, quiz_counts_data = get_quiz_count_by_subject()
    registration_labels, registration_data = get_user_registration_trend()
    avg_quiz_labels, avg_quiz_data = get_average_score_by_quiz()

    context = {
        "subjects": subjects_with_chapters,
        "subject_labels": subject_labels,
        "quiz_counts_data": quiz_counts_data,
        "registration_labels": registration_labels,
        "registration_data": registration_data,
        "avg_quiz_labels": avg_quiz_labels,
        "avg_quiz_data": avg_quiz_data,
    }

    return render_template("admin/dashboard.html", **context)


@admin_bp.route("/users")
@admin_required
def users():
    """Displays a list of registered users with search functionality."""
    search_term = request.args.get("search", "")
    query = User.query

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    user_list = query.order_by(User.full_name).all()
    return render_template("admin/users.html", users=user_list, search_term=search_term)


# --- Subject Management Routes ---


@admin_bp.route("/subjects")
@admin_required
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

    subject_list = query.order_by(Subject.name).all()
    return render_template(
        "admin/subjects.html", subjects=subject_list, search_term=search_term
    )


@admin_bp.route("/subject/add", methods=["GET", "POST"])
@admin_required
def add_subject():
    """Handles adding a new subject."""
    form = SubjectForm()
    if form.validate_on_submit():
        existing_subject = Subject.query.filter(
            func.lower(Subject.name) == func.lower(form.name.data)
        ).first()
        if existing_subject:
            flash(f"Subject '{form.name.data}' already exists.", "warning")
        else:
            try:
                new_subject = Subject(
                    name=form.name.data, description=form.description.data
                )
                db.session.add(new_subject)
                db.session.commit()
                flash("Subject added successfully.", "success")
                return redirect(url_for("admin.subjects"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding subject: {e}", "danger")

    return render_template("admin/subject_form.html", form=form, title="Add Subject")


@admin_bp.route("/subject/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_subject(id):
    """Handles editing an existing subject."""
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        new_name_lower = form.name.data.lower()
        conflicting_subject = Subject.query.filter(
            func.lower(Subject.name) == new_name_lower, Subject.id != id
        ).first()

        if conflicting_subject:
            flash(
                f"Another subject with the name '{form.name.data}' already exists.",
                "warning",
            )
        else:
            try:
                subject.name = form.name.data
                subject.description = form.description.data
                db.session.commit()
                flash("Subject updated successfully.", "success")
                return redirect(url_for("admin.subjects"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating subject: {e}", "danger")

    return render_template("admin/subject_form.html", form=form, title="Edit Subject")


@admin_bp.route("/subject/delete/<int:id>", methods=["POST"])
@admin_required
def delete_subject(id):
    """Handles deleting a subject."""
    subject = Subject.query.get_or_404(id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(
            f"Error deleting subject: {e}. Ensure no chapters depend on it.", "danger"
        )
    return redirect(url_for("admin.subjects"))


# --- Chapter Management Routes ---


@admin_bp.route("/chapters/<int:subject_id>")
@admin_required
def chapters(subject_id):
    """Displays chapters for a specific subject."""
    subject = Subject.query.get_or_404(subject_id)
    chapter_list = (
        Chapter.query.filter_by(subject_id=subject_id).order_by(Chapter.name).all()
    )
    return render_template(
        "admin/chapters.html", chapters=chapter_list, subject=subject
    )


@admin_bp.route("/chapter/add/<int:subject_id>", methods=["GET", "POST"])
@admin_required
def add_chapter(subject_id):
    """Handles adding a new chapter to a subject."""
    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm()

    if form.validate_on_submit():
        existing_chapter = Chapter.query.filter(
            Chapter.subject_id == subject_id,
            func.lower(Chapter.name) == func.lower(form.name.data),
        ).first()
        if existing_chapter:
            flash(
                f"Chapter '{form.name.data}' already exists in this subject.", "warning"
            )
        else:
            try:
                new_chapter = Chapter(
                    name=form.name.data,
                    description=form.description.data,
                    subject_id=subject_id,
                )
                db.session.add(new_chapter)
                db.session.commit()
                flash("Chapter added successfully.", "success")
                return redirect(url_for("admin.chapters", subject_id=subject_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding chapter: {e}", "danger")

    return render_template(
        "admin/chapter_form.html", form=form, subject=subject, title="Add Chapter"
    )


@admin_bp.route("/chapter/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_chapter(id):
    """Handles editing an existing chapter."""
    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)

    if form.validate_on_submit():
        new_name_lower = form.name.data.lower()
        conflicting_chapter = Chapter.query.filter(
            Chapter.subject_id == chapter.subject_id,
            func.lower(Chapter.name) == new_name_lower,
            Chapter.id != id,
        ).first()
        if conflicting_chapter:
            flash(
                f"Another chapter with the name '{form.name.data}' already exists in this subject.",
                "warning",
            )
        else:
            try:
                chapter.name = form.name.data
                chapter.description = form.description.data
                db.session.commit()
                flash("Chapter updated successfully.", "success")
                return redirect(
                    url_for("admin.chapters", subject_id=chapter.subject_id)
                )
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating chapter: {e}", "danger")

    return render_template(
        "admin/chapter_form.html",
        form=form,
        subject=chapter.subject,
        title="Edit Chapter",
    )


@admin_bp.route("/chapter/delete/<int:id>", methods=["POST"])
@admin_required
def delete_chapter(id):
    """Handles deleting a chapter."""
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    try:
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting chapter: {e}. Ensure no quizzes depend on it.", "danger")
    return redirect(url_for("admin.chapters", subject_id=subject_id))


# --- Quiz Management Routes ---


@admin_bp.route("/quizzes/<int:chapter_id>")
@admin_required
def quizzes(chapter_id):
    """Displays quizzes for a specific chapter with search."""
    chapter = Chapter.query.get_or_404(chapter_id)
    search_term = request.args.get("search", "")
    query = Quiz.query.filter_by(chapter_id=chapter_id)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Quiz.remarks.ilike(search_pattern))

    quiz_list = query.order_by(Quiz.date_of_quiz.desc()).all()
    return render_template(
        "admin/quizzes.html",
        quizzes=quiz_list,
        chapter=chapter,
        search_term=search_term,
    )


@admin_bp.route("/quiz/add/<int:chapter_id>", methods=["GET", "POST"])
@admin_required
def add_quiz(chapter_id):
    """Handles adding a new quiz to a chapter."""
    chapter = Chapter.query.get_or_404(chapter_id)
    form = QuizForm()

    if form.validate_on_submit():
        try:
            time_parts = form.time_duration.data.split(":")
            if len(time_parts) != 2:
                raise ValueError("Invalid time format")
            duration_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            if duration_minutes <= 0:
                raise ValueError("Duration must be positive")

            new_quiz = Quiz(
                chapter_id=chapter_id,
                date_of_quiz=form.date_of_quiz.data,
                time_duration=duration_minutes,
                remarks=form.remarks.data,
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash("Quiz added successfully.", "success")
            return redirect(url_for("admin.quizzes", chapter_id=chapter_id))
        except (ValueError, IndexError, TypeError) as e:
            flash(
                f"Invalid time format or value. Please use HH:MM and ensure duration is positive. Error: {e}",
                "danger",
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding quiz: {e}", "danger")

    return render_template(
        "admin/quiz_form.html", form=form, chapter=chapter, title="Add Quiz"
    )


@admin_bp.route("/quiz/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_quiz(id):
    """Handles editing an existing quiz."""
    quiz = Quiz.query.get_or_404(id)
    form = QuizForm()

    if form.validate_on_submit():
        try:
            time_parts = form.time_duration.data.split(":")
            if len(time_parts) != 2:
                raise ValueError("Invalid time format")
            duration_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            if duration_minutes <= 0:
                raise ValueError("Duration must be positive")

            quiz.date_of_quiz = form.date_of_quiz.data
            quiz.time_duration = duration_minutes
            quiz.remarks = form.remarks.data

            db.session.commit()
            flash("Quiz updated successfully.", "success")
            return redirect(url_for("admin.quizzes", chapter_id=quiz.chapter_id))
        except (ValueError, IndexError, TypeError) as e:
            flash(
                f"Invalid time format or value. Please use HH:MM and ensure duration is positive. Error: {e}",
                "danger",
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating quiz: {e}", "danger")

    if request.method == "GET" or not form.validate():
        form.date_of_quiz.data = quiz.date_of_quiz
        form.remarks.data = quiz.remarks
        hours, minutes = divmod(quiz.time_duration, 60)
        form.time_duration.data = f"{hours:02d}:{minutes:02d}"

    return render_template(
        "admin/quiz_form.html", form=form, chapter=quiz.chapter, title="Edit Quiz"
    )


@admin_bp.route("/quiz/delete/<int:id>", methods=["POST"])
@admin_required
def delete_quiz(id):
    """Handles deleting a quiz."""
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash("Quiz deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting quiz: {e}. Ensure no questions depend on it.", "danger")
    return redirect(url_for("admin.quizzes", chapter_id=chapter_id))


# --- Question Management Routes ---


@admin_bp.route("/questions/<int:quiz_id>")
@admin_required
def questions(quiz_id):
    """Displays questions for a specific quiz with search."""
    quiz = Quiz.query.get_or_404(quiz_id)
    search_term = request.args.get("search", "")
    query = Question.query.filter_by(quiz_id=quiz_id)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Question.question_text.ilike(search_pattern))

    question_list = query.order_by(Question.id).all()
    return render_template(
        "admin/questions.html",
        questions=question_list,
        quiz=quiz,
        search_term=search_term,
    )


@admin_bp.route("/question/add/<int:quiz_id>", methods=["GET", "POST"])
@admin_required
def add_question(quiz_id):
    """Handles adding a new question to a quiz."""
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()

    if form.validate_on_submit():
        correct_answer_int = get_correct_answer_int(form.correct_option.data)

        if correct_answer_int is None:
            flash("Invalid correct option selected.", "danger")
        else:
            try:
                new_question = Question(
                    quiz_id=quiz_id,
                    question_text=form.question_text.data,
                    option1=form.option1.data,
                    option2=form.option2.data,
                    option3=form.option3.data,
                    option4=form.option4.data,
                    correct_answer=correct_answer_int,
                )
                db.session.add(new_question)
                db.session.commit()
                flash("Question added successfully.", "success")
                return redirect(url_for("admin.questions", quiz_id=quiz_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding question: {e}", "danger")

    return render_template(
        "admin/question_form.html", form=form, quiz=quiz, title="Add Question"
    )


# Helper function to map option string to integer
def get_correct_answer_int(option_string):
    """Maps form option string ('option1', etc.) to integer (1, etc.)."""
    mapping = {"option1": 1, "option2": 2, "option3": 3, "option4": 4}
    return mapping.get(option_string)


# Helper function to map integer to option string
def get_correct_option_string(answer_int):
    """Maps integer answer (1, etc.) to form option string ('option1', etc.)."""
    mapping = {1: "option1", 2: "option2", 3: "option3", 4: "option4"}
    return mapping.get(answer_int)


@admin_bp.route("/question/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_question(id):
    """Handles editing an existing question."""
    question = Question.query.get_or_404(id)
    form = QuestionForm()

    if form.validate_on_submit():
        new_correct_answer = get_correct_answer_int(form.correct_option.data)

        if new_correct_answer is None:
            flash("Invalid correct option selected.", "danger")
        else:
            try:
                question.question_text = form.question_text.data
                question.option1 = form.option1.data
                question.option2 = form.option2.data
                question.option3 = form.option3.data
                question.option4 = form.option4.data
                question.correct_answer = new_correct_answer

                db.session.commit()
                flash("Question updated successfully.", "success")
                return redirect(url_for("admin.questions", quiz_id=question.quiz_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating question: {e}", "danger")

    if request.method == "GET" or not form.validate():
        form.question_text.data = question.question_text
        form.option1.data = question.option1
        form.option2.data = question.option2
        form.option3.data = question.option3
        form.option4.data = question.option4
        form.correct_option.data = get_correct_option_string(question.correct_answer)

    return render_template(
        "admin/question_form.html", form=form, quiz=question.quiz, title="Edit Question"
    )


@admin_bp.route("/question/delete/<int:id>", methods=["POST"])
@admin_required
def delete_question(id):
    """Handles deleting a question."""
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    try:
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting question: {e}", "danger")
    return redirect(url_for("admin.questions", quiz_id=quiz_id))
