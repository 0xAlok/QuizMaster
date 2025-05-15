from app import db
from datetime import datetime

class Subject(db.Model):
    """Represents a subject area containing chapters and quizzes."""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """Provides a developer-friendly representation of the Subject object."""
        return f'<Subject {self.name}>'
