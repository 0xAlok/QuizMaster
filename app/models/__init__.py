# Import models here
from app.models.user import User, Admin
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score

# Export all models for easier importing
__all__ = ['User', 'Admin', 'Subject', 'Chapter', 'Quiz', 'Question', 'Score']