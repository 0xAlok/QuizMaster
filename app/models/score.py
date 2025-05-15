from app import db
from datetime import datetime

class Score(db.Model):
    """Represents a score achieved by a user on a specific quiz attempt."""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_scored = db.Column(db.Integer, nullable=False, default=0) 
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow, index=True) 
    
    def __repr__(self):
        """Provides a developer-friendly representation of the Score object."""
        return f'<Score {self.id} User {self.user_id} Quiz {self.quiz_id}>'
