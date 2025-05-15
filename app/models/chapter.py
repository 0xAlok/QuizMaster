from app import db
from datetime import datetime

class Chapter(db.Model):
    """Represents a chapter within a subject, containing quizzes."""
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """Provides a developer-friendly representation of the Chapter object."""
        return f'<Chapter {self.name}>'
