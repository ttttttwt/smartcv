from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import db

class User(UserMixin, db.Model):
    """Model người dùng"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship với CV
    cvs = db.relationship('CV', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Mã hóa mật khẩu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)
    
    def get_cv_count(self):
        """Đếm số CV của user"""
        return len(self.cvs)
    
    def get_recent_cvs(self, limit=5):
        """Lấy CV gần đây"""
        return sorted(self.cvs, key=lambda x: x.updated_at, reverse=True)[:limit]
    
    def __repr__(self):
        return f'<User {self.username}>'


