from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from db import db
import json

class CVTemplate(db.Model):
    """Model for CV Templates"""
    __tablename__ = 'cv_templates'
    
    id = db.Column(db.String(50), primary_key=True)  # e.g., 'modern', 'professional'
    name = db.Column(db.String(100), nullable=False)  # Display name
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='modern')  # modern, professional, creative, minimal
    template = db.Column(db.Text)  # Template configuration or HTML template
    preview_image = db.Column(db.String(200))  # Path to preview image
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    features = db.Column(db.Text)  # JSON array of features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_features(self):
        """Get features as list"""
        if self.features:
            try:
                return json.loads(self.features)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_features(self, features_list):
        """Set features from list"""
        self.features = json.dumps(features_list)
    
    def get_template_data(self):
        """Get template data as dict compatible with canvas editor"""
        if self.template:
            try:
                return json.loads(self.template)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_template_data(self, template_dict):
        """Set template data from dict (canvas editor format)"""
        self.template = json.dumps(template_dict, ensure_ascii=False)
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        db.session.commit()
    
    def get_popularity_badge(self):
        """Get popularity badge based on usage"""
        if self.usage_count > 1000:
            return {'text': 'Phổ biến', 'class': 'bg-amber-400 text-amber-900'}
        elif self.usage_count > 500:
            return {'text': 'Được yêu thích', 'class': 'bg-green-400 text-green-900'}
        elif self.created_at and (datetime.utcnow() - self.created_at).days < 30:
            return {'text': 'Mới', 'class': 'bg-purple-500 text-white'}
        return None
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template': self.get_template_data(),
            'preview_image': self.preview_image,
            'usage_count': self.usage_count,
            'features': self.get_features(),
            'popularity_badge': self.get_popularity_badge()
        }
    
    @staticmethod
    def seed_default_templates():
        """Create default templates if they don't exist"""
        default_templates = [
            {
                'id': 'modern_complete',
                'name': 'Modern Complete CV',
                'description': 'Template hiện đại hoàn chỉnh với đầy đủ các thành phần CV chuyên nghiệp',
                'category': 'modern',
                'features': ['Full Layout', 'Professional Design', 'Header Section', 'Skills Visual', 'Modern Colors'],
                'usage_count': 0,
                'template_data': {
                    'attrs': {
                        'width': 595,
                        'height': 842
                    },
                    'className': 'Stage',
                    'children': [
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'width': 595,
                                        'height': 120,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'header_bg'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 170,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'summary_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 280,
                                        'width': 4,
                                        'height': 160,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'experience_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 490,
                                        'width': 4,
                                        'height': 100,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'skills_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 620,
                                        'width': 4,
                                        'height': 120,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'education_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 770,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#3B82F6',
                                        'strokeWidth': 0,
                                        'id': 'languages_border'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 25,
                                        'text': '{{full_name}}',
                                        'fontSize': 28,
                                        'fontStyle': 'bold',
                                        'fill': '#FFFFFF',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'full_name'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 65,
                                        'text': '{{position}}',
                                        'fontSize': 16,
                                        'fill': '#E5E7EB',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 30,
                                        'text': '✉ {{email}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'email'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 50,
                                        'text': '📞 {{phone}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'phone'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 70,
                                        'text': '📍 {{address}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'address'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 150,
                                        'text': 'MÔ TẢ BẢN THÂN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'summary_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 175,
                                        'text': '{{summary}}',
                                        'fontSize': 11,
                                        'fill': '#4B5563',
                                        'width': 500,
                                        'height': 50,
                                        'lineHeight': 1.2,
                                        'id': 'summary'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 260,
                                        'text': 'KINH NGHIỆM LÀM VIỆC',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'experience_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 285,
                                        'text': '{{experience[0].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 305,
                                        'text': '{{experience[0].company}}',
                                        'fontSize': 11,
                                        'fill': '#3B82F6',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 285,
                                        'text': '{{experience[0].start_date}} - {{experience[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 325,
                                        'text': '{{experience[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 375,
                                        'text': '{{experience[1].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 395,
                                        'text': '{{experience[1].company}}',
                                        'fontSize': 11,
                                        'fill': '#3B82F6',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 375,
                                        'text': '{{experience[1].start_date}} - {{experience[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 415,
                                        'text': '{{experience[1].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp2_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 470,
                                        'text': 'KỸ NĂNG',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 495,
                                        'text': 'Kỹ năng chuyên môn',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 495,
                                        'text': 'Kỹ năng mềm',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 515,
                                        'text': '• {{technical_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 530,
                                        'text': '• {{technical_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 545,
                                        'text': '• {{technical_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 515,
                                        'text': '• {{soft_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 530,
                                        'text': '• {{soft_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 545,
                                        'text': '• {{soft_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 600,
                                        'text': 'HỌC VẤN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'education_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 625,
                                        'text': '{{education[0].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 645,
                                        'text': '{{education[0].school}}',
                                        'fontSize': 11,
                                        'fill': '#3B82F6',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 625,
                                        'text': '{{education[0].start_date}} - {{education[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 665,
                                        'text': '{{education[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 30,
                                        'lineHeight': 1.2,
                                        'id': 'edu1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 705,
                                        'text': '{{education[1].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 725,
                                        'text': '{{education[1].school}}',
                                        'fontSize': 11,
                                        'fill': '#3B82F6',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 705,
                                        'text': '{{education[1].start_date}} - {{education[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 750,
                                        'text': 'NGÔN NGỮ',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'languages_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 775,
                                        'text': '• {{languages[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 775,
                                        'text': '• {{languages[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_2'
                                    },
                                    'className': 'Text'
                                }
                            ]
                        }
                    ]
                }
            },
            {
                'id': 'modern_green',
                'name': 'Modern Green CV',
                'description': 'Template hiện đại với tông màu xanh lá cây tươi mát, phù hợp cho các ngành sáng tạo và môi trường',
                'category': 'modern',
                'features': ['Full Layout', 'Eco Design', 'Header Section', 'Skills Visual', 'Green Theme'],
                'usage_count': 0,
                'template_data': {
                    'attrs': {
                        'width': 595,
                        'height': 842
                    },
                    'className': 'Stage',
                    'children': [
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'width': 595,
                                        'height': 120,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'header_bg'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 170,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'summary_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 280,
                                        'width': 4,
                                        'height': 160,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'experience_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 490,
                                        'width': 4,
                                        'height': 100,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'skills_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 620,
                                        'width': 4,
                                        'height': 120,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'education_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 770,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#10B981',
                                        'strokeWidth': 0,
                                        'id': 'languages_border'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 25,
                                        'text': '{{full_name}}',
                                        'fontSize': 28,
                                        'fontStyle': 'bold',
                                        'fill': '#FFFFFF',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'full_name'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 65,
                                        'text': '{{position}}',
                                        'fontSize': 16,
                                        'fill': '#E5E7EB',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 30,
                                        'text': '✉ {{email}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'email'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 50,
                                        'text': '📞 {{phone}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'phone'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 70,
                                        'text': '📍 {{address}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'address'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 150,
                                        'text': 'MÔ TẢ BẢN THÂN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'summary_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 175,
                                        'text': '{{summary}}',
                                        'fontSize': 11,
                                        'fill': '#4B5563',
                                        'width': 500,
                                        'height': 50,
                                        'lineHeight': 1.2,
                                        'id': 'summary'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 260,
                                        'text': 'KINH NGHIỆM LÀM VIỆC',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'experience_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 285,
                                        'text': '{{experience[0].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 305,
                                        'text': '{{experience[0].company}}',
                                        'fontSize': 11,
                                        'fill': '#10B981',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 285,
                                        'text': '{{experience[0].start_date}} - {{experience[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 325,
                                        'text': '{{experience[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 375,
                                        'text': '{{experience[1].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 395,
                                        'text': '{{experience[1].company}}',
                                        'fontSize': 11,
                                        'fill': '#10B981',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 375,
                                        'text': '{{experience[1].start_date}} - {{experience[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 415,
                                        'text': '{{experience[1].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp2_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 470,
                                        'text': 'KỸ NĂNG',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 495,
                                        'text': 'Kỹ năng chuyên môn',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 495,
                                        'text': 'Kỹ năng mềm',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 515,
                                        'text': '• {{technical_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 530,
                                        'text': '• {{technical_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 545,
                                        'text': '• {{technical_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 515,
                                        'text': '• {{soft_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 530,
                                        'text': '• {{soft_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 545,
                                        'text': '• {{soft_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 600,
                                        'text': 'HỌC VẤN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'education_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 625,
                                        'text': '{{education[0].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 645,
                                        'text': '{{education[0].school}}',
                                        'fontSize': 11,
                                        'fill': '#10B981',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 625,
                                        'text': '{{education[0].start_date}} - {{education[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 665,
                                        'text': '{{education[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 30,
                                        'lineHeight': 1.2,
                                        'id': 'edu1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 705,
                                        'text': '{{education[1].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 725,
                                        'text': '{{education[1].school}}',
                                        'fontSize': 11,
                                        'fill': '#10B981',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 705,
                                        'text': '{{education[1].start_date}} - {{education[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#6B7280',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 750,
                                        'text': 'NGÔN NGỮ',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'languages_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 775,
                                        'text': '• {{languages[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 775,
                                        'text': '• {{languages[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_2'
                                    },
                                    'className': 'Text'
                                }
                            ]
                        }
                    ]
                }
            },
            {
                'id': 'modern_gray',
                'name': 'Modern Gray CV',
                'description': 'Template hiện đại với tông màu xám thanh lịch, phù hợp cho môi trường công sở chuyên nghiệp',
                'category': 'professional',
                'features': ['Full Layout', 'Minimal Design', 'Header Section', 'Skills Visual', 'Gray Theme'],
                'usage_count': 0,
                'template_data': {
                    'attrs': {
                        'width': 595,
                        'height': 842
                    },
                    'className': 'Stage',
                    'children': [
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'width': 595,
                                        'height': 120,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'header_bg'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 170,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'summary_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 280,
                                        'width': 4,
                                        'height': 160,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'experience_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 490,
                                        'width': 4,
                                        'height': 100,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'skills_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 620,
                                        'width': 4,
                                        'height': 120,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'education_border'
                                    },
                                    'className': 'Rect'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 770,
                                        'width': 4,
                                        'height': 60,
                                        'fill': '#6B7280',
                                        'strokeWidth': 0,
                                        'id': 'languages_border'
                                    },
                                    'className': 'Rect'
                                }
                            ]
                        },
                        {
                            'attrs': {},
                            'className': 'Layer',
                            'children': [
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 25,
                                        'text': '{{full_name}}',
                                        'fontSize': 28,
                                        'fontStyle': 'bold',
                                        'fill': '#FFFFFF',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'full_name'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 65,
                                        'text': '{{position}}',
                                        'fontSize': 16,
                                        'fill': '#E5E7EB',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 30,
                                        'text': '✉ {{email}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'email'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 50,
                                        'text': '📞 {{phone}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'phone'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 70,
                                        'text': '📍 {{address}}',
                                        'fontSize': 11,
                                        'fill': '#FFFFFF',
                                        'width': 150,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'address'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 150,
                                        'text': 'MÔ TẢ BẢN THÂN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'summary_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 175,
                                        'text': '{{summary}}',
                                        'fontSize': 11,
                                        'fill': '#4B5563',
                                        'width': 500,
                                        'height': 50,
                                        'lineHeight': 1.2,
                                        'id': 'summary'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 260,
                                        'text': 'KINH NGHIỆM LÀM VIỆC',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'experience_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 285,
                                        'text': '{{experience[0].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 305,
                                        'text': '{{experience[0].company}}',
                                        'fontSize': 11,
                                        'fill': '#6B7280',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 285,
                                        'text': '{{experience[0].start_date}} - {{experience[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#9CA3AF',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 325,
                                        'text': '{{experience[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 375,
                                        'text': '{{experience[1].position}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_position'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 395,
                                        'text': '{{experience[1].company}}',
                                        'fontSize': 11,
                                        'fill': '#6B7280',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_company'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 375,
                                        'text': '{{experience[1].start_date}} - {{experience[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#9CA3AF',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'exp2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 415,
                                        'text': '{{experience[1].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 40,
                                        'lineHeight': 1.2,
                                        'id': 'exp2_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 470,
                                        'text': 'KỸ NĂNG',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 495,
                                        'text': 'Kỹ năng chuyên môn',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 495,
                                        'text': 'Kỹ năng mềm',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#374151',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skills_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 515,
                                        'text': '• {{technical_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 530,
                                        'text': '• {{technical_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 545,
                                        'text': '• {{technical_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'tech_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 515,
                                        'text': '• {{soft_skills[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 530,
                                        'text': '• {{soft_skills[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_2'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 545,
                                        'text': '• {{soft_skills[2]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'soft_skill_3'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 600,
                                        'text': 'HỌC VẤN',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'education_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 625,
                                        'text': '{{education[0].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 645,
                                        'text': '{{education[0].school}}',
                                        'fontSize': 11,
                                        'fill': '#6B7280',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 625,
                                        'text': '{{education[0].start_date}} - {{education[0].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#9CA3AF',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu1_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 75,
                                        'y': 665,
                                        'text': '{{education[0].description}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 480,
                                        'height': 30,
                                        'lineHeight': 1.2,
                                        'id': 'edu1_description'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 705,
                                        'text': '{{education[1].degree}}',
                                        'fontSize': 12,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_degree'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 725,
                                        'text': '{{education[1].school}}',
                                        'fontSize': 11,
                                        'fill': '#6B7280',
                                        'width': 350,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_school'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 420,
                                        'y': 705,
                                        'text': '{{education[1].start_date}} - {{education[1].end_date}}',
                                        'fontSize': 10,
                                        'fill': '#9CA3AF',
                                        'width': 135,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'edu2_date'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 40,
                                        'y': 750,
                                        'text': 'NGÔN NGỮ',
                                        'fontSize': 14,
                                        'fontStyle': 'bold',
                                        'fill': '#1F2937',
                                        'width': 515,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'languages_title'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 55,
                                        'y': 775,
                                        'text': '• {{languages[0]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 250,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_1'
                                    },
                                    'className': 'Text'
                                },
                                {
                                    'attrs': {
                                        'x': 320,
                                        'y': 775,
                                        'text': '• {{languages[1]}}',
                                        'fontSize': 10,
                                        'fill': '#4B5563',
                                        'width': 235,
                                        'wrap': 'none',
                                        'lineHeight': 1.2,
                                        'id': 'language_2'
                                    },
                                    'className': 'Text'
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        
        for template_data in default_templates:
            existing = CVTemplate.query.get(template_data['id'])
            if not existing:
                template = CVTemplate(
                    id=template_data['id'],
                    name=template_data['name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    usage_count=template_data['usage_count']
                )
                template.set_features(template_data['features'])
                template.set_template_data(template_data['template_data'])
                db.session.add(template)
            else:
                # Update existing template with new data including education section
                existing.set_template_data(template_data['template_data'])
        
        db.session.commit()
    
    def __repr__(self):
        return f'<CVTemplate {self.name}>'
