from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
from models.user import User
from db import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Đăng nhập người dùng"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validation
        if not email or not password:
            flash('Vui lòng điền đầy đủ thông tin đăng nhập.', 'error')
            return render_template('auth/login.html')
        
        # Tìm user trong database
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember_me)
            flash(f'Chào mừng {user.username}!', 'success')
            
            # Redirect to dashboard hoặc trang được yêu cầu
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email hoặc mật khẩu không chính xác.', 'error')
    
    return render_template('auth/login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký tài khoản mới"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Lấy dữ liệu form
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        agree_terms = request.form.get('agree_terms') == 'on'
        
        # Validation
        errors = []
        
        if not full_name or len(full_name) < 2:
            errors.append('Họ tên phải có ít nhất 2 ký tự.')
        
        if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append('Email không hợp lệ.')
        
        if not password or len(password) < 8:
            errors.append('Mật khẩu phải có ít nhất 8 ký tự.')
        
        if password != confirm_password:
            errors.append('Mật khẩu xác nhận không khớp.')
        
        if not agree_terms:
            errors.append('Bạn cần đồng ý với điều khoản sử dụng.')
        
        # Kiểm tra email đã tồn tại
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors.append('Email này đã được sử dụng.')
        
        # Kiểm tra username đã tồn tại
        existing_username = User.query.filter_by(username=full_name).first()
        if existing_username:
            errors.append('Tên người dùng này đã được sử dụng.')
        
        if phone and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', phone):
            errors.append('Số điện thoại không hợp lệ.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Tạo user mới trong database
        try:
            new_user = User(
                username=full_name,
                email=email
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Tài khoản đã được tạo thành công! Chào mừng {full_name}.', 'success')
            
            # Tự động đăng nhập sau khi đăng ký
            login_user(new_user)
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@user_bp.route('/logout')
@login_required
def logout():
    """Đăng xuất người dùng"""
    user_name = current_user.username
    logout_user()
    flash(f'Tạm biệt {user_name}! Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('main.index'))

@user_bp.route('/profile')
@login_required
def profile():
    """Trang thông tin cá nhân"""
    return render_template('profile.html', user=current_user)

@user_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Cập nhật thông tin cá nhân"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    
    # Validation
    errors = []
    
    if not username or len(username) < 2:
        errors.append('Họ tên phải có ít nhất 2 ký tự.')
    
    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errors.append('Email không hợp lệ.')
    
    # Kiểm tra email đã tồn tại (trừ email hiện tại)
    existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        errors.append('Email này đã được sử dụng bởi tài khoản khác.')
    
    # Kiểm tra username đã tồn tại (trừ username hiện tại)
    existing_username = User.query.filter(User.username == username, User.id != current_user.id).first()
    if existing_username:
        errors.append('Tên người dùng này đã được sử dụng.')
    
    if phone and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', phone):
        errors.append('Số điện thoại không hợp lệ.')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('user.profile'))
    
    # Cập nhật thông tin
    try:
        current_user.username = username
        current_user.email = email
        current_user.phone = phone if phone else None
        
        db.session.commit()
        flash('Thông tin cá nhân đã được cập nhật thành công!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi cập nhật thông tin. Vui lòng thử lại.', 'error')
    
    return redirect(url_for('user.profile'))

@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Đổi mật khẩu"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    errors = []
    
    if not current_password:
        errors.append('Vui lòng nhập mật khẩu hiện tại.')
    elif not current_user.check_password(current_password):
        errors.append('Mật khẩu hiện tại không chính xác.')
    
    if not new_password or len(new_password) < 8:
        errors.append('Mật khẩu mới phải có ít nhất 8 ký tự.')
    
    if new_password != confirm_password:
        errors.append('Mật khẩu xác nhận không khớp.')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('user.profile'))
    
    # Cập nhật mật khẩu
    try:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Mật khẩu đã được thay đổi thành công!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi đổi mật khẩu. Vui lòng thử lại.', 'error')
    
    return redirect(url_for('user.profile'))

@user_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Quên mật khẩu"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Vui lòng nhập địa chỉ email.', 'error')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Email không hợp lệ.', 'error')
        else:
            # Kiểm tra email có tồn tại không
            user = User.query.filter_by(email=email).first()
            if user:
                # TODO: Implement email sending
                flash('Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.', 'success')
            else:
                flash('Email không tồn tại trong hệ thống.', 'error')
            return redirect(url_for('user.login'))
    
    return render_template('auth/forgot_password.html')
