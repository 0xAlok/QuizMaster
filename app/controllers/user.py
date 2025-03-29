from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date # Import date
from app import db
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from sqlalchemy import func, cast, Date # Import func for count/avg, cast/Date for grouping

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Decorator to ensure only regular users (not admins) access user routes
def user_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, User):
            flash('This page is for regular users only', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def dashboard():
    # Get available subjects for the user
    subjects = Subject.query.all()
    # Get user's past quiz attempts, ordered chronologically for the chart
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt.asc()).all() # Order ascending for score trend chart
    
    # --- Get Upcoming Quizzes ---
    today = date.today()
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= today).order_by(Quiz.date_of_quiz.asc()).limit(10).all() # Limit for dashboard view

    # --- Prepare data for Score Trend Chart ---
    # Pass timestamps (milliseconds) for the time scale
    score_labels = [score.time_stamp_of_attempt.timestamp() * 1000 for score in scores] 
    score_data = [score.total_scored for score in scores]

    # --- Prepare data for Average Score per Subject Chart ---
    avg_scores_per_subject = db.session.query(
            Subject.name,
            func.avg(Score.total_scored)
        ).select_from(Score)\
        .join(Quiz, Score.quiz_id == Quiz.id)\
        .join(Chapter, Quiz.chapter_id == Chapter.id)\
        .join(Subject, Chapter.subject_id == Subject.id)\
        .filter(Score.user_id == current_user.id)\
        .group_by(Subject.name)\
        .order_by(Subject.name)\
        .all()
    avg_score_subject_labels = [item[0] for item in avg_scores_per_subject]
    avg_score_subject_data = [round(item[1], 1) if item[1] is not None else 0 for item in avg_scores_per_subject]

    # --- Prepare data for Attempts per Subject Chart ---
    attempts_per_subject = db.session.query(
            Subject.name,
            func.count(Score.id)
        ).select_from(Score)\
        .join(Quiz, Score.quiz_id == Quiz.id)\
        .join(Chapter, Quiz.chapter_id == Chapter.id)\
        .join(Subject, Chapter.subject_id == Subject.id)\
        .filter(Score.user_id == current_user.id)\
        .group_by(Subject.name)\
        .order_by(Subject.name)\
        .all()
    attempt_subject_labels = [item[0] for item in attempts_per_subject]
    attempt_subject_data = [item[1] for item in attempts_per_subject]
    
    # --- Calculate overall stats (using the same scores list) ---
    total_attempts = len(scores)
    average_score = 0
    if total_attempts > 0:
        average_score = sum(score.total_scored for score in scores) / total_attempts
    
    return render_template('user/dashboard.html', 
                           subjects=subjects,
                           scores=scores, # Pass original scores list too if needed elsewhere
                           total_attempts=total_attempts,
                           average_score=average_score,
                           # Chart data
                           score_labels=score_labels, 
                           score_data=score_data,
                           avg_score_subject_labels=avg_score_subject_labels, 
                           avg_score_subject_data=avg_score_subject_data,   
                           attempt_subject_labels=attempt_subject_labels, 
                           attempt_subject_data=attempt_subject_data,
                           # Pass upcoming quizzes
                           upcoming_quizzes=upcoming_quizzes,
                           # Pass the actual list of Score objects for the table 
                           # (already passed earlier in the argument list)
                           )     

@user_bp.route('/subjects')
@user_required
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
        
    subjects = query.all()
    return render_template('user/subjects.html', subjects=subjects, search_term=search_term)

@user_bp.route('/subject/<int:subject_id>/chapters')
@user_required
def chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('user/chapters.html', subject=subject, chapters=chapters)

@user_bp.route('/chapter/<int:chapter_id>/quizzes')
@user_required
def quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    search_term = request.args.get('search', '')
    query = Quiz.query.filter_by(chapter_id=chapter_id)
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Quiz.remarks.ilike(search_pattern))
        
    quizzes = query.all()
    today = datetime.now().date()
    return render_template('user/quizzes.html', 
                           chapter=chapter, 
                           quizzes=quizzes, 
                           today=today, 
                           search_term=search_term)

@user_bp.route('/quiz/<int:quiz_id>/start')
@user_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is available for today
    if quiz.date_of_quiz != datetime.now().date():
        flash('This quiz is not available today.', 'danger')
        return redirect(url_for('user.quizzes', chapter_id=quiz.chapter_id))
    
    # Check if user has already attempted this quiz
    previous_attempt = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    return render_template('user/start_quiz.html', quiz=quiz, previous_attempt=previous_attempt)

@user_bp.route('/quiz/<int:quiz_id>/attempt')
@user_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions.', 'warning')
        return redirect(url_for('user.start_quiz', quiz_id=quiz_id))
    
    # Set up quiz timer in session
    session['quiz_start_time'] = datetime.now().timestamp()
    session['quiz_end_time'] = session['quiz_start_time'] + (quiz.time_duration * 60)  # Convert minutes to seconds
    
    return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions)

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@user_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Calculate score
    total_questions = len(questions)
    correct_answers = 0
    results = {}
    
    for question in questions:
        question_id = str(question.id)
        selected_answer = request.form.get(f'question_{question_id}', None)
        
        if selected_answer:
            selected_answer = int(selected_answer)
            is_correct = (selected_answer == question.correct_answer)
            if is_correct:
                correct_answers += 1
            
            results[question_id] = {
                'selected': selected_answer,
                'correct': question.correct_answer,
                'is_correct': is_correct
            }
    
    # Calculate percentage
    score_percentage = 0
    if total_questions > 0:
        score_percentage = (correct_answers / total_questions) * 100
    
    # Save score to database
    score = Score(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_scored=score_percentage,
        time_stamp_of_attempt=datetime.now()
    )
    db.session.add(score)
    db.session.commit()
    
    # Clear quiz session data
    if 'quiz_start_time' in session:
        session.pop('quiz_start_time')
    if 'quiz_end_time' in session:
        session.pop('quiz_end_time')
    
    return render_template('user/quiz_result.html', 
                          quiz=quiz, 
                          questions=questions, 
                          results=results, 
                          score=score_percentage,
                          correct_answers=correct_answers,
                          total_questions=total_questions)

@user_bp.route('/quiz/check-time')
@user_required
def check_quiz_time():
    """AJAX endpoint to check remaining quiz time"""
    if 'quiz_end_time' not in session:
        return jsonify({'time_remaining': 0, 'expired': True})
    
    current_time = datetime.now().timestamp()
    end_time = session['quiz_end_time']
    remaining = end_time - current_time
    
    return jsonify({
        'time_remaining': max(0, int(remaining)),
        'expired': remaining <= 0
    })

@user_bp.route('/history')
@user_required
def history():
    """Show user's quiz attempt history with filtering"""
    # Get filter parameters from query string
    search_term = request.args.get('search', '')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    # Base query
    query = Score.query.filter_by(user_id=current_user.id)

    # Apply text search filter (on Subject or Chapter name)
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.join(Quiz).join(Chapter).join(Subject).filter(
            db.or_(
                Subject.name.ilike(search_pattern),
                Chapter.name.ilike(search_pattern)
                # Could also search Quiz.remarks if needed
            )
        )

    # Apply score range filter
    if min_score is not None:
        query = query.filter(Score.total_scored >= min_score)
    if max_score is not None:
        query = query.filter(Score.total_scored <= max_score)

    # Apply date range filter
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Filter scores from the beginning of the start date
            query = query.filter(Score.time_stamp_of_attempt >= datetime.combine(start_date, datetime.min.time()))
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
             # Filter scores until the end of the end date
            query = query.filter(Score.time_stamp_of_attempt <= datetime.combine(end_date, datetime.max.time()))
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
        start_date_str = '' # Reset invalid date strings
        end_date_str = ''

    # Execute query and order
    scores = query.order_by(Score.time_stamp_of_attempt.desc()).all()
    
    return render_template('user/history.html', 
                           scores=scores,
                           search_term=search_term,
                           min_score=min_score,
                           max_score=max_score,
                           start_date=start_date_str,
                           end_date=end_date_str)
