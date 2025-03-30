from app import db
from datetime import datetime

class Question(db.Model):
    """Represents a single question within a quiz."""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)  # Stores the correct option number (1, 2, 3, or 4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """Provides a developer-friendly representation of the Question object."""
        return f'<Question {self.id} for Quiz {self.quiz_id}>'
