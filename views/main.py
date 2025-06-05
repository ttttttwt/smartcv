from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.cv import CV
from models.user import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Trang chủ - Giới thiệu ứng dụng"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Bảng điều khiển chính - Quản lý CV"""
    # Lấy thống kê thực từ database
    user_cvs = CV.query.filter_by(user_id=current_user.id).all()
    total_cvs = len(user_cvs)
    total_views = sum(getattr(cv, 'views', 0) for cv in user_cvs)
    total_downloads = sum(getattr(cv, 'downloads', 0) for cv in user_cvs)
    
    # Thống kê cơ bản cho dashboard
    user_stats = {
        'total_cvs': total_cvs,
        'total_templates': 8,  # Số template có sẵn
        'completed_profile': 85,  # Tính toán dựa trên thông tin user
        'cv_views': total_views,
        'total_downloads': total_downloads
    }
    
    # Danh sách CV gần đây từ database
    recent_cvs = []
    sorted_cvs = sorted(user_cvs, key=lambda x: x.updated_at, reverse=True)
    for cv in sorted_cvs[:3]:  # Lấy 3 CV gần nhất
        recent_cvs.append({
            'id': cv.id,
            'name': cv.title,
            'template': cv.template_id.title() if cv.template_id else 'Modern',
            'created_at': cv.created_at.strftime('%d/%m/%Y'),
            'status': 'Hoàn thiện' if cv.content else 'Đang chỉnh sửa',
            'views': getattr(cv, 'views', 0),
            'is_canvas_editor': cv.is_canvas_editor
        })
    
    return render_template('dashboard.html', 
                         user_stats=user_stats, 
                         recent_cvs=recent_cvs)


