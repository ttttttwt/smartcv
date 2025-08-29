import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from db import db

# Load environment variables
load_dotenv()

# Initialize other extensions
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///smart_cv.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from views.cv import cv_bp
    from views.main import main_bp
    from views.user import user_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cv_bp)
    
    # Create database tables
    with app.app_context():
        # Import models để tạo tables
        from models.cv import CV
        from models.cv_template import CVTemplate
        from models.user import User
        
        db.create_all()
        
        # Tạo user admin mẫu nếu chưa có
        admin_user = User.query.filter_by(email='admin@smartcv.com').first()
        if not admin_user:
            admin = User(username='admin', email='admin@smartcv.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Seed default templates
        CVTemplate.seed_default_templates()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

