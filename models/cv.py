from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import db
import json

class CV(db.Model):
    """Model CV"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='CV mới')
    content = db.Column(db.Text)  # JSON content của CV
    template_id = db.Column(db.String(50), default='modern_complete')  # Add template_id field
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)  # Track downloads
    is_canvas_editor = db.Column(db.Boolean, default=False)  # Track canvas editor usage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def set_content(self, content_dict):
        """Lưu content dạng JSON"""
        self.content = json.dumps(content_dict, ensure_ascii=False)
    
    def get_content(self):
        """Lấy content từ JSON"""
        if self.content:
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def increment_views(self):
        """Tăng số lượt xem"""
        self.views += 1
        db.session.commit()
    
    def increment_downloads(self):
        """Tăng số lượt tải xuống"""
        self.downloads += 1
        db.session.commit()
    
    def set_canvas_edited(self):
        """Đánh dấu CV đã được chỉnh sửa bằng canvas editor"""
        self.is_canvas_editor = True
        db.session.commit()
    
    def get_template_name(self):
        """Get template display name"""
        if self.template_id:
            return f'Template {self.template_id.replace("_", " ").title()}'
        return 'Template mặc định'
        
    def get_form_data(self):
        """Lấy form_data từ content (nếu có)"""
        content = self.get_content()
        if content and isinstance(content, dict):
            return content.get('form_data')
        return None

    def __repr__(self):
        return f'<CV {self.title}>'