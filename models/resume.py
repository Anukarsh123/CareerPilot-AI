import json
from datetime import datetime
from extensions import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_json = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship("User", backref=db.backref("resumes", lazy=True, cascade="all, delete-orphan"))

    def set_parsed_data(self, data_dict):
        """Helper to serialize structured data dictionary into JSON string."""
        self.parsed_json = json.dumps(data_dict)

    def get_parsed_data(self):
        """Helper to deserialize JSON string into dictionary."""
        if self.parsed_json:
            try:
                return json.loads(self.parsed_json)
            except json.JSONDecodeError:
                return {}
        return {}