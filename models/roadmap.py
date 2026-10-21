import json
from datetime import datetime
from extensions import db

class CareerRoadmap(db.Model):
    __tablename__ = "career_roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    milestones_json = db.Column(db.Text, nullable=False)  # JSON string of stages & tasks
    github_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("roadmaps", lazy=True, cascade="all, delete-orphan"))

    def set_milestones(self, milestones_list):
        self.milestones_json = json.dumps(milestones_list)

    def get_milestones(self):
        return json.loads(self.milestones_json) if self.milestones_json else []