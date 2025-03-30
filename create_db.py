from app import create_app, db
from app.models.user import Admin, User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from datetime import date, timedelta, datetime

def add_sample_data():
    """Adds sample data if it doesn't already exist."""
    print("Checking for existing sample data...")

    # Check if sample user exists
    sample_user_email = 'testuser@example.com'
    sample_user = User.query.filter_by(username=sample_user_email).first()

    if sample_user:
        print("Sample data seems to exist already. Skipping creation.")
        return

    print("Creating sample data...")
    try:
        # 1. Sample User
        print("- Creating sample user...")
        user1 = User(username=sample_user_email, full_name='Test User', qualification='Tester', dob=date(2000, 1, 1))
        user1.set_password('password')
        db.session.add(user1)
        # We need the user ID later, so commit here to get it assigned
        db.session.commit()
        print(f"  User '{user1.username}' created with ID {user1.id}")

        # 2. Subjects
        print("- Creating subjects...")
        maths = Subject(name='Mathematics', description='Basic mathematical concepts and problems.')
        history = Subject(name='History', description='Overview of significant world events.')
        db.session.add_all([maths, history])
        # Commit to get subject IDs
        db.session.commit()
        print(f"  Subject '{maths.name}' created with ID {maths.id}")
        print(f"  Subject '{history.name}' created with ID {history.id}")

        # 3. Chapters
        print("- Creating chapters...")
        algebra = Chapter(subject_id=maths.id, name='Algebra Basics', description='Introduction to algebraic expressions and equations.')
        ww1 = Chapter(subject_id=history.id, name='World War I', description='Causes, events, and consequences of the Great War.')
        db.session.add_all([algebra, ww1])
        # Commit to get chapter IDs
        db.session.commit()
        print(f"  Chapter '{algebra.name}' created with ID {algebra.id}")
        print(f"  Chapter '{ww1.name}' created with ID {ww1.id}")

        # 4. Quizzes
        print("- Creating quizzes...")
        today = date.today()
        tomorrow = today + timedelta(days=1)
        quiz_alg1 = Quiz(chapter_id=algebra.id, date_of_quiz=today, time_duration=5, remarks='Basic algebra check')
        quiz_ww1_1 = Quiz(chapter_id=ww1.id, date_of_quiz=today, time_duration=5, remarks='Key events of WWI')
        quiz_ww1_2 = Quiz(chapter_id=ww1.id, date_of_quiz=tomorrow, time_duration=10, remarks='More details on WWI')
        db.session.add_all([quiz_alg1, quiz_ww1_1, quiz_ww1_2])
        # Commit to get quiz IDs
        db.session.commit()
        print(f"  Quiz Alg#1 created with ID {quiz_alg1.id}")
        print(f"  Quiz WWI#1 created with ID {quiz_ww1_1.id}")
        print(f"  Quiz WWI#2 created with ID {quiz_ww1_2.id}")

        # 5. Questions
        print("- Creating questions...")
        # Algebra Quiz 1
        q_alg1_1 = Question(quiz_id=quiz_alg1.id, question_text='What is 2 + 2?', option1='3', option2='4', option3='5', option4='6', correct_answer=2)
        q_alg1_2 = Question(quiz_id=quiz_alg1.id, question_text='What is x if x + 3 = 5?', option1='1', option2='2', option3='3', option4='4', correct_answer=2)
        # WWI Quiz 1
        q_ww1_1_1 = Question(quiz_id=quiz_ww1_1.id, question_text='When did WWI start?', option1='1912', option2='1914', option3='1916', option4='1918', correct_answer=2)
        q_ww1_1_2 = Question(quiz_id=quiz_ww1_1.id, question_text='Which event triggered WWI?', option1='Pearl Harbor', option2='D-Day', option3='Assassination of Archduke Ferdinand', option4='Boston Tea Party', correct_answer=3)
        # WWI Quiz 2
        q_ww1_2_1 = Question(quiz_id=quiz_ww1_2.id, question_text='Which country was NOT a Central Power?', option1='Germany', option2='Austria-Hungary', option3='Ottoman Empire', option4='France', correct_answer=4)
        q_ww1_2_2 = Question(quiz_id=quiz_ww1_2.id, question_text='What treaty ended WWI?', option1='Treaty of Paris', option2='Treaty of Ghent', option3='Treaty of Versailles', option4='Treaty of Tordesillas', correct_answer=3)
        q_ww1_2_3 = Question(quiz_id=quiz_ww1_2.id, question_text='What year did WWI end?', option1='1917', option2='1918', option3='1919', option4='1920', correct_answer=2)
        db.session.add_all([q_alg1_1, q_alg1_2, q_ww1_1_1, q_ww1_1_2, q_ww1_2_1, q_ww1_2_2, q_ww1_2_3])

        # 6. Scores
        print("- Creating sample scores...")
        score1 = Score(quiz_id=quiz_alg1.id, user_id=user1.id, total_scored=50, time_stamp_of_attempt=datetime.utcnow() - timedelta(hours=1))
        score2 = Score(quiz_id=quiz_ww1_1.id, user_id=user1.id, total_scored=100, time_stamp_of_attempt=datetime.utcnow())
        db.session.add_all([score1, score2])

        # Final commit for questions and scores
        db.session.commit()
        print("Sample data created successfully.")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")


def init_db():
    """
    Initializes the database by creating all tables defined in the models
    and ensures a default admin user and sample data exist.
    """
    print("Initializing database...")
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        # Drop existing tables first for a clean slate (optional, use with caution)
        # print("Dropping existing tables (if any)...")
        # db.drop_all()
        db.create_all()
        print("Tables created.")

        # --- Create Default Admin ---
        admin_username = 'admin@quizmaster.com'
        existing_admin = Admin.query.filter_by(username=admin_username).first()

        if not existing_admin:
            print(f"Creating default admin user: {admin_username}")
            try:
                default_admin = Admin(username=admin_username)
                default_admin.set_password('admin')
                db.session.add(default_admin)
                db.session.commit()
                print('Default admin user created successfully.')
            except Exception as e:
                db.session.rollback()
                print(f"Error creating default admin user: {e}")
        else:
            print(f"Admin user '{admin_username}' already exists.")

        # --- Add Sample Data ---
        add_sample_data()

        print('Database initialization process completed.')

if __name__ == '__main__':
    init_db()
