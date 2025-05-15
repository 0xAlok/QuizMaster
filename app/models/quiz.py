from app import db
from datetime import datetime

class Quiz(db.Model):
    """Represents a quiz belonging to a chapter, containing questions and scores."""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration stored in minutes
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """Provides a developer-friendly representation of the Quiz object."""
        return f'<Quiz {self.id} for Chapter {self.chapter_id}>'
