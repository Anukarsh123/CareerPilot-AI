from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    target_role = db.Column(db.String(100), nullable=True)
    xp_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    github_username = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def role(self):
        return (self.target_role or "user").strip() or "user"

    @property
    def display_name(self):
        return (self.full_name or self.username or "CareerPilot User").strip() or self.username or "CareerPilot User"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)