from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import Admin, User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score # Import Score model
from app.controllers.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from datetime import datetime # Ensure datetime is imported
from sqlalchemy import func # Import func for count

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Decorator to check if user is an admin
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash("You must be an admin to access this page", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


from sqlalchemy.orm import joinedload # Import joinedload for eager loading

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Decorator to check if user is an admin
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash("You must be an admin to access this page", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    # Fetch subjects and eagerly load their chapters
    subjects_with_chapters = Subject.query.options(joinedload(Subject.chapters)).order_by(Subject.name).all()
    
    # Keep chart data queries for now, might be used later or removed from template
    # Data for quizzes per subject chart
    quizzes_per_subject = db.session.query(
            Subject.name, 
            func.count(Quiz.id)
        ).select_from(Subject)\
        .outerjoin(Chapter, Subject.id == Chapter.subject_id)\
        .outerjoin(Quiz, Chapter.id == Quiz.chapter_id)\
        .group_by(Subject.name)\
        .order_by(Subject.name)\
        .all()
        
    subject_labels = [item[0] for item in quizzes_per_subject]
    quiz_counts_data = [item[1] for item in quizzes_per_subject]
    
    # Data for User Registration Trend
    # Group by date - adjust DB function if needed for specific DB (e.g., DATE() for SQLite)
    users_per_day = db.session.query(
            func.DATE(User.created_at), # Group by date part only
            func.count(User.id)
        ).select_from(User)\
        .group_by(func.DATE(User.created_at))\
        .order_by(func.DATE(User.created_at))\
        .all()
    registration_labels = [datetime.strptime(item[0], '%Y-%m-%d').strftime('%Y-%m-%d') for item in users_per_day if item[0]] 
    registration_data = [item[1] for item in users_per_day]

    # Data for Average Score per Quiz
    avg_score_per_quiz = db.session.query(
            Quiz.id, # Use Quiz ID or maybe Chapter/Subject name for label?
            func.avg(Score.total_scored)
        ).select_from(Score)\
        .join(Quiz, Score.quiz_id == Quiz.id)\
        .group_by(Quiz.id)\
        .order_by(Quiz.id)\
        .all()
    avg_quiz_labels = [f"Quiz #{item[0]}" for item in avg_score_per_quiz] 
    avg_quiz_data = [round(item[1], 1) if item[1] is not None else 0 for item in avg_score_per_quiz]


    return render_template(
        "admin/dashboard.html",
        subjects=subjects_with_chapters, # Pass subjects with chapters
        # Pass chart data (can be removed later if charts are removed from template)
        subject_labels=subject_labels, 
        quiz_counts_data=quiz_counts_data,
        registration_labels=registration_labels, # User Reg Trend Labels
        registration_data=registration_data,     # User Reg Trend Data
        avg_quiz_labels=avg_quiz_labels,         # Avg Score/Quiz Labels
        avg_quiz_data=avg_quiz_data              # Avg Score/Quiz Data
    )

@admin_bp.route("/users")
@admin_required
def users():
    search_term = request.args.get('search', '')
    query = User.query
    
    if search_term:
        search_pattern = f"%{search_term}%"
        # Assuming User model has 'username' and 'full_name' fields
        query = query.filter(
            db.or_(
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )
        
    users_list = query.all()
    return render_template("admin/users.html", users=users_list, search_term=search_term)


# Subject Management Routes
@admin_bp.route("/subjects")
@admin_required
def subjects():
    search_term = request.args.get('search', '')
    query = Subject.query
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Subject.name.ilike(search_pattern),
                Subject.description.ilike(search_pattern)
            )
        )
        
    subjects_list = query.all()
    return render_template("admin/subjects.html", subjects=subjects_list, search_term=search_term)


@admin_bp.route("/subject/add", methods=["GET", "POST"])
@admin_required
def add_subject():
    form = SubjectForm()

    if form.validate_on_submit():
        subject = Subject(name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully", "success")
        return redirect(url_for("admin.subjects"))

    return render_template("admin/subject_form.html", form=form, title="Add Subject")


@admin_bp.route("/subject/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject updated successfully", "success")
        return redirect(url_for("admin.subjects"))

    return render_template("admin/subject_form.html", form=form, title="Edit Subject")


@admin_bp.route("/subject/delete/<int:id>", methods=["POST"])
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully", "success")
    return redirect(url_for("admin.subjects"))


# Chapter Management Routes
@admin_bp.route("/chapters/<int:subject_id>")
@admin_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters_list = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template(
        "admin/chapters.html", chapters=chapters_list, subject=subject
    )


@admin_bp.route("/chapter/add/<int:subject_id>", methods=["GET", "POST"])
@admin_required
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm()

    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=subject_id,
        )
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter added successfully", "success")
        return redirect(url_for("admin.chapters", subject_id=subject_id))

    return render_template(
        "admin/chapter_form.html", form=form, subject=subject, title="Add Chapter"
    )


@admin_bp.route("/chapter/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)

    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        db.session.commit()
        flash("Chapter updated successfully", "success")
        return redirect(url_for("admin.chapters", subject_id=chapter.subject_id))

    return render_template(
        "admin/chapter_form.html",
        form=form,
        subject=chapter.subject,
        title="Edit Chapter",
    )


@admin_bp.route("/chapter/delete/<int:id>", methods=["POST"])
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully", "success")
    return redirect(url_for("admin.chapters", subject_id=subject_id))


# Quiz Management Routes
@admin_bp.route("/quizzes/<int:chapter_id>")
@admin_required
def quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    search_term = request.args.get('search', '')
    query = Quiz.query.filter_by(chapter_id=chapter_id)
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Quiz.remarks.ilike(search_pattern))
        
    quizzes_list = query.all()
    return render_template("admin/quizzes.html", 
                           quizzes=quizzes_list, 
                           chapter=chapter, 
                           search_term=search_term)


@admin_bp.route("/quiz/add/<int:chapter_id>", methods=["GET", "POST"])
@admin_required
def add_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = QuizForm()

    if form.validate_on_submit():
        # Parse time_duration string (HH:MM) into minutes for storage
        time_parts = form.time_duration.data.split(":")
        duration_minutes = int(time_parts[0]) * 60 + int(time_parts[1])

        quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=form.date_of_quiz.data,
            time_duration=duration_minutes,  # Store as minutes in the database
            remarks=form.remarks.data,
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz added successfully", "success")
        return redirect(url_for("admin.quizzes", chapter_id=chapter_id))

    return render_template(
        "admin/quiz_form.html", form=form, chapter=chapter, title="Add Quiz"
    )


@admin_bp.route("/quiz/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    # Initialize the form without obj to avoid overwriting custom fields
    form = QuizForm()

    if form.validate_on_submit():
        # Parse time_duration string (HH:MM) into minutes for storage
        try:
            time_parts = form.time_duration.data.split(":")
            duration_minutes = int(time_parts[0]) * 60 + int(time_parts[1])

            quiz.date_of_quiz = form.date_of_quiz.data
            quiz.time_duration = duration_minutes
            quiz.remarks = form.remarks.data

            db.session.commit()
            flash("Quiz updated successfully", "success")
            return redirect(url_for("admin.quizzes", chapter_id=quiz.chapter_id))
        except (ValueError, IndexError) as e:
            flash(f"Invalid time format. Please use HH:MM format.", "danger")

    # For GET requests or form validation failure, populate the form
    if not form.is_submitted():
        form.date_of_quiz.data = quiz.date_of_quiz
        form.remarks.data = quiz.remarks

        # Format the time duration as HH:MM for the form
        hours, minutes = divmod(quiz.time_duration, 60)
        form.time_duration.data = f"{hours:02d}:{minutes:02d}"

    return render_template(
        "admin/quiz_form.html", form=form, chapter=quiz.chapter, title="Edit Quiz"
    )


@admin_bp.route("/quiz/delete/<int:id>", methods=["POST"])
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully", "success")
    return redirect(url_for("admin.quizzes", chapter_id=chapter_id))


# Question Management Routes
@admin_bp.route("/questions/<int:quiz_id>")
@admin_required
def questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    search_term = request.args.get('search', '')
    query = Question.query.filter_by(quiz_id=quiz_id)
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Question.question_text.ilike(search_pattern))
        
    questions_list = query.all()
    return render_template("admin/questions.html", 
                           questions=questions_list, 
                           quiz=quiz, 
                           search_term=search_term)


@admin_bp.route("/question/add/<int:quiz_id>", methods=["GET", "POST"])
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()

    if form.validate_on_submit():
        # Determine correct answer
        correct_answer = None
        if form.correct_option.data == "option1":
            correct_answer = 1
        elif form.correct_option.data == "option2":
            correct_answer = 2
        elif form.correct_option.data == "option3":
            correct_answer = 3
        elif form.correct_option.data == "option4":
            correct_answer = 4

        question = Question(
            quiz_id=quiz_id,
            question_text=form.question_text.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_answer=correct_answer,
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added successfully", "success")
        return redirect(url_for("admin.questions", quiz_id=quiz_id))

    return render_template(
        "admin/question_form.html", form=form, quiz=quiz, title="Add Question"
    )


@admin_bp.route("/question/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    form = QuestionForm(obj=question)

    # Set the correct_option radio button based on the correct_answer value
    if question.correct_answer == 1:
        form.correct_option.data = "option1"
    elif question.correct_answer == 2:
        form.correct_option.data = "option2"
    elif question.correct_answer == 3:
        form.correct_option.data = "option3"
    elif question.correct_answer == 4:
        form.correct_option.data = "option4"

    if form.validate_on_submit():
        # Determine correct answer
        correct_answer = None
        if form.correct_option.data == "option1":
            correct_answer = 1
        elif form.correct_option.data == "option2":
            correct_answer = 2
        elif form.correct_option.data == "option3":
            correct_answer = 3
        elif form.correct_option.data == "option4":
            correct_answer = 4

        question.question_text = form.question_text.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_answer = correct_answer

        db.session.commit()
        flash("Question updated successfully", "success")
        return redirect(url_for("admin.questions", quiz_id=question.quiz_id))

    return render_template(
        "admin/question_form.html", form=form, quiz=question.quiz, title="Edit Question"
    )


@admin_bp.route("/question/delete/<int:id>", methods=["POST"])
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully", "success")
    return redirect(url_for("admin.questions", quiz_id=quiz_id))
