import json
from datetime import datetime
from extensions import db

class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default="Medium")
    questions_json = db.Column(db.Text, nullable=False)  # List of questions
    responses_json = db.Column(db.Text, nullable=True)   # User answers & feedback
    overall_score = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("interviews", lazy=True, cascade="all, delete-orphan"))

    def set_questions(self, questions_list):
        self.questions_json = json.dumps(questions_list)

    def get_questions(self):
        return json.loads(self.questions_json) if self.questions_json else []

    def set_responses(self, responses_dict):
        self.responses_json = json.dumps(responses_dict)

    def get_responses(self):
        return json.loads(self.responses_json) if self.responses_json else {}