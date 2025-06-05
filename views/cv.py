from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
from models.cv import CV
from models.user import User
from models.cv_template import CVTemplate
from db import db
import json
import re
import tempfile
import os
import copy
import traceback
from utils.pdf_generator import KonvaJSONToPDF
from utils.cv_utils import *
from utils.ai_cv import *
from typing import Dict, List, Any, Optional

cv_bp = Blueprint('cv', __name__, url_prefix='/cv')
ai = GeminiAI()

@cv_bp.route('/list')
@login_required
def cv_list():
    """Hiển thị danh sách CV của người dùng với tìm kiếm và lọc"""
    try:
        # Lấy tham số tìm kiếm và lọc
        search_query = request.args.get('search', '').strip()
        template_filter = request.args.get('template', '').strip()
        sort_by = request.args.get('sort', 'newest')
        
        # Base query
        query = CV.query.filter_by(user_id=current_user.id)
        
        # Apply search filter
        if search_query:
            # Search in title and content
            search_pattern = f'%{search_query}%'
            query = query.filter(
                db.or_(
                    CV.title.ilike(search_pattern),
                    CV.content.ilike(search_pattern)
                )
            )
        
        # Apply template filter
        if template_filter:
            query = query.filter(CV.template_id.ilike(f'%{template_filter}%'))
        
        # Apply sorting
        if sort_by == 'oldest':
            query = query.order_by(CV.created_at.asc())
        elif sort_by == 'name':
            query = query.order_by(CV.title.asc())
        elif sort_by == 'views':
            query = query.order_by(CV.views.desc())
        elif sort_by == 'downloads':
            query = query.order_by(CV.downloads.desc())
        else:  # newest (default)
            query = query.order_by(CV.updated_at.desc())
        
        cvs = query.all()
        
        # Lấy danh sách templates có sẵn
        available_templates = CVTemplate.query.filter(CVTemplate.is_active == True).all()
        
        # Lấy danh sách template_ids đã được sử dụng bởi user
        used_template_ids = db.session.query(CV.template_id).filter_by(user_id=current_user.id).distinct().all()
        used_template_ids = [t[0] for t in used_template_ids if t[0]]
        
        # Format dữ liệu để hiển thị
        cv_list = []
        for cv in cvs:
            content = cv.get_content()
            form_data = content.get('form_data', {})
            
            # Lấy tên template từ database
            template_name = 'Template mặc định'
            if cv.template_id:
                template = CVTemplate.query.get(cv.template_id)
                if template:
                    template_name = template.name
                else:
                    template_name = cv.template_id.replace('_', ' ').title()
            
            cv_data = {
                'id': cv.id,
                'name': cv.title,
                'title': cv.title,
                'template': template_name,
                'template_id': cv.template_id,
                'views': cv.views,
                'downloads': cv.downloads,
                'updated_at': format_time_ago(cv.updated_at),
                'created_at': format_time_ago(cv.created_at),
                'full_name': form_data.get('full_name', 'Chưa có tên'),
                'position': form_data.get('position', 'Chưa có vị trí'),
                'is_canvas_editor': cv.is_canvas_editor
            }
            cv_list.append(cv_data)
        
        # Thống kê tổng quan
        all_cvs = CV.query.filter_by(user_id=current_user.id).all()
        total_views = sum(cv.views for cv in all_cvs)
        total_downloads = sum(cv.downloads for cv in all_cvs)
        
        stats = {
            'total_cvs': len(all_cvs),
            'total_views': total_views,
            'total_downloads': total_downloads
        }
        
        return render_template('cv/cv_list.html', 
                             cvs=cv_list, 
                             stats=stats,
                             available_templates=available_templates,
                             used_template_ids=used_template_ids,
                             current_search=search_query,
                             current_template=template_filter,
                             current_sort=sort_by)
    
    except Exception as e:
        flash('Có lỗi xảy ra khi tải danh sách CV. Vui lòng thử lại.', 'error')
        return render_template('cv/cv_list.html', cvs=[], stats={}, available_templates=[], used_template_ids=[])

@cv_bp.route('/create')
@login_required
def create_cv():
    """Trang tạo CV mới"""
    template = request.args.get('template', 'modern')
    
    # Tạo CV mẫu với template được chọn
    cv_data = None
    if template:
        flash(f'Đã chọn template: {template.title()}', 'info')
    
    return render_template('cv/cv_form.html', cv=cv_data, template=template)


@cv_bp.route('/<int:cv_id>/edit')
@login_required
def edit_cv_form(cv_id):
    """Trang chỉnh sửa CV với form"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            flash('Không tìm thấy CV hoặc bạn không có quyền truy cập.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Lấy form_data từ content hoặc tạo mới nếu chưa có
        form_data = cv.get_form_data()
        if not form_data:
            # Trích xuất dữ liệu từ template data nếu không có form_data
            content = cv.get_content()
            template_data = content.get('template_data', {})
            if template_data:
                form_data = extract_cv_data_from_template_data(cv, content)
            else:
                form_data = {}
        
        # Format dữ liệu để hiển thị trong form
        cv_data = {
            'id': cv.id,
            'title': cv.title,
            'template_id': cv.template_id,
            **form_data  # Merge form_data vào cv_data
        }
        
        return render_template('cv/cv_form.html', cv=cv_data, edit_mode=True)
        
    except Exception as e:
        print(f"Error in edit_cv_form: {str(e)}")  # For debugging
        flash('Có lỗi xảy ra khi tải thông tin CV.', 'error')
        return redirect(url_for('cv.cv_list'))

@cv_bp.route('/<int:cv_id>/update', methods=['POST'])
@login_required
def update_cv_form(cv_id):
    """Xử lý cập nhật CV từ form"""
    try:
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            error_msg = 'Không tìm thấy CV hoặc bạn không có quyền truy cập.'
            if is_ajax:
                return jsonify({'success': False, 'error': error_msg}), 404
            flash(error_msg, 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Lấy dữ liệu từ form
        form_data = request.form.to_dict(flat=False)
        
        # Reformat single-item lists to strings for simple fields
        for key, value in form_data.items():
            if isinstance(value, list) and len(value) == 1 and not key.endswith('[]'):
                form_data[key] = value[0]
        
        # Validate dữ liệu
        errors = validate_cv_data(form_data)
        if errors:
            if is_ajax:
                return jsonify({'success': False, 'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('cv.edit_cv_form', cv_id=cv_id))
        
        # Lấy content hiện tại của CV
        current_content = cv.get_content()
        
        # Chuẩn bị dữ liệu form update với structured data
        form_updates = {
            'title': form_data.get('title', cv.title),
            'full_name': form_data.get('full_name', ''),
            'position': form_data.get('position', ''),
            'email': form_data.get('email', ''),
            'phone': form_data.get('phone', ''),
            'address': form_data.get('address', ''),
            'website': form_data.get('website', ''),
            'summary': form_data.get('summary', ''),
            'experience': build_experience_data(form_data),
            'education': build_education_data(form_data),
            'technical_skills': form_data.get('technical_skills[]', []),
            'soft_skills': form_data.get('soft_skills[]', []),
            'languages': form_data.get('languages[]', [])
        }
        
        # Sử dụng CVDataUpdater để cập nhật dữ liệu
        updater = CVDataUpdater()
        updated_content = updater.update_cv_data(current_content, form_updates)
        
        # Cập nhật title của CV nếu có thay đổi
        new_title = form_updates.get('title')
        if new_title and new_title != cv.title:
            cv.title = new_title
        
        # Lưu content đã cập nhật vào CV
        cv.set_content(updated_content)
        cv.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        success_msg = 'CV đã được cập nhật thành công!'
        if is_ajax:
            return jsonify({
                'success': True,
                'message': success_msg,
                'redirect_url': url_for('cv.cv_preview', cv_id=cv_id)
            })
        
        flash(success_msg, 'success')
        return redirect(url_for('cv.cv_preview', cv_id=cv_id))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating CV: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = 'Có lỗi xảy ra khi cập nhật CV. Vui lòng thử lại.'
        if is_ajax:
            return jsonify({'success': False, 'error': error_msg}), 500
        
        flash(error_msg, 'error')
        return redirect(url_for('cv.edit_cv_form', cv_id=cv_id))

@cv_bp.route('/<int:cv_id>/preview')
@login_required
def cv_preview(cv_id):
    """Xem trước CV với dữ liệu thực tế"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            flash('Không tìm thấy CV hoặc bạn không có quyền truy cập.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Tăng lượt xem
        cv.increment_views()
        
        # Lấy content và xử lý dữ liệu
        content = cv.get_content()
        
        # Lấy tham số source để chọn nguồn dữ liệu (mặc định là template_data)
        data_source = request.args.get('source', 'template_data')
        
        # Chuẩn bị dữ liệu CV theo nguồn được chọn
        if data_source == 'form_data':
            cv_data = extract_cv_data_from_form_data(cv, content)
        else:  # Mặc định là template_data
            cv_data = extract_cv_data_from_template_data(cv, content)
        
        # Kiểm tra và chuẩn bị template_data cho JSON serialization
        if data_source != 'form_data' and 'template_data' in content:
            # Đảm bảo template_data có thể serialize thành JSON
            try:
                import json
                # Test serialization trước
                json.dumps(content.get('template_data', {}))
                template_data = content.get('template_data', {})
            except TypeError:
                # Nếu có lỗi, sử dụng object rỗng thay thế
                template_data = {}
                print("Warning: template_data không thể serializable, sử dụng object rỗng.")
        else:
            template_data = {}
            
        # Gán template_data đã được kiểm tra vào cv_data
        cv_data['template_data'] = template_data
        cv_data['is_canvas_editor'] = cv.is_canvas_editor  # Thêm thông tin về editor
        
        # Trả về template xem trước CV
        return render_template('cv/cv_preview.html', 
                             cv=cv_data, 
                             data_source=data_source)
        
    except Exception as e:
        print(f"Error in cv_preview: {str(e)}")  # For debugging
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging
        flash('Có lỗi xảy ra khi tải CV. Vui lòng thử lại.', 'error')
        return redirect(url_for('cv.cv_list'))

@cv_bp.route('/templates')
@login_required
def template_selector():
    """Trang chọn template CV với dữ liệu từ database"""
    try:
        # Lấy tham số lọc và tìm kiếm
        category_filter = request.args.get('category', 'all')
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'popular')  # popular, newest, rating
        
        # Query templates từ database
        query = CVTemplate.query.filter(CVTemplate.is_active == True)
        
        # Lọc theo category
        if category_filter != 'all':
            query = query.filter(CVTemplate.category == category_filter)
        
        # Tìm kiếm theo tên hoặc mô tả
        if search_query:
            search_pattern = f'%{search_query}%'
            query = query.filter(
                db.or_(
                    CVTemplate.name.ilike(search_pattern),
                    CVTemplate.description.ilike(search_pattern)
                )
            )
        
        # Sắp xếp
        if sort_by == 'newest':
            query = query.order_by(CVTemplate.created_at.desc())
        elif sort_by == 'rating':
            query = query.order_by(CVTemplate.rating.desc(), CVTemplate.rating_count.desc())
        else:  # popular (default)
            query = query.order_by(CVTemplate.usage_count.desc())
        
        templates = query.all()
        
        # Lấy danh sách categories có sẵn
        categories = db.session.query(CVTemplate.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Thống kê templates
        stats = {
            'total_templates': len(templates),
            'categories_count': len(categories),
            'popular_templates': [t for t in templates if t.usage_count > 500]
        }
        
        return render_template('cv/template_selector.html', 
                             templates=templates,
                             categories=categories,
                             stats=stats,
                             current_category=category_filter,
                             current_search=search_query,
                             current_sort=sort_by)
    
    except Exception as e:
        print(f"Error in template_selector: {str(e)}")
        flash('Có lỗi xảy ra khi tải danh sách template. Vui lòng thử lại.', 'error')
        
        # Fallback to default templates
        CVTemplate.seed_default_templates()
        templates = CVTemplate.query.filter(CVTemplate.is_active == True).all()
        return render_template('cv/template_selector.html', 
                             templates=templates,
                             categories=['modern', 'professional', 'creative', 'minimal'],
                             stats={'total_templates': len(templates)})

@cv_bp.route('/api/templates')
@login_required
def api_templates():
    """API endpoint để lấy danh sách templates"""
    try:
        category = request.args.get('category', 'all')
        
        query = CVTemplate.query.filter(CVTemplate.is_active == True)
        if category != 'all':
            query = query.filter(CVTemplate.category == category)
        
        templates = query.order_by(CVTemplate.usage_count.desc()).all()
        
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates],
            'total': len(templates)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Có lỗi xảy ra khi tải templates.'
        })

@cv_bp.route('/api/templates/<template_id>/preview')
@login_required
def api_template_preview(template_id):
    """API để lấy thông tin preview của template"""
    try:
        template = CVTemplate.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template không tồn tại.'
            })
        
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Có lỗi xảy ra khi tải preview.'
        })

@cv_bp.route('/api/templates/<template_id>/select', methods=['POST'])
@login_required
def api_select_template(template_id):
    """API để chọn template và track usage"""
    try:
        template = CVTemplate.query.get(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template không tồn tại.'
            })
        
        # Track template selection (không tăng usage_count ở đây, 
        # sẽ tăng khi CV thực sự được tạo)
        
        return jsonify({
            'success': True,
            'message': f'Đã chọn template {template.name}',
            'redirect_url': url_for('cv.create_cv', template=template_id),
            'template': template.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Có lỗi xảy ra khi chọn template.'
        })

@cv_bp.route('/<int:cv_id>/duplicate')
@login_required
def duplicate_cv(cv_id):
    """Sao chép CV"""
    try:
        # Lấy CV gốc
        original_cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not original_cv:
            flash('Không tìm thấy CV hoặc bạn không có quyền truy cập.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Tạo bản sao
        new_cv = CV(
            title=f"Bản sao - {original_cv.title}",
            content=original_cv.content,  # Copy content
            template_id=original_cv.template_id,
            user_id=current_user.id,
            is_canvas_editor=original_cv.is_canvas_editor  # Copy editor type
        )
        
        db.session.add(new_cv)
        db.session.commit()
        
        flash('CV đã được sao chép thành công!', 'success')
        
        # Redirect based on editor type
        if original_cv.is_canvas_editor:
            return redirect(url_for('cv.cv_preview', cv_id=new_cv.id))
        else:
            return redirect(url_for('cv.edit_cv_form', cv_id=new_cv.id))
        
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi sao chép CV.', 'error')
        return redirect(url_for('cv.cv_list'))

@cv_bp.route('/<int:cv_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_cv(cv_id):
    """Xóa CV (phiên bản hợp nhất duy nhất)"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            if request.method == 'POST' or request.is_json:
                return jsonify({'success': False, 'error': 'Không tìm thấy CV hoặc bạn không có quyền xóa.'})
            flash('Không tìm thấy CV hoặc bạn không có quyền xóa.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Lưu tên CV để thông báo
        cv_title = cv.title
        
        # Xóa CV
        db.session.delete(cv)
        db.session.commit()
        
        if request.method == 'POST' or request.is_json:
            return jsonify({
                'success': True, 
                'message': f'CV "{cv_title}" đã được xóa thành công!'
            })
        
        flash(f'CV "{cv_title}" đã được xóa thành công!', 'success')
        return redirect(url_for('cv.cv_list'))
        
    except Exception as e:
        db.session.rollback()
        if request.method == 'POST' or request.is_json:
            return jsonify({'success': False, 'error': 'Có lỗi xảy ra khi xóa CV.'})
        print(f"Error deleting CV: {str(e)}")  # For debugging
        flash('Có lỗi xảy ra khi xóa CV.', 'error')
        return redirect(url_for('cv.cv_list'))

@cv_bp.route('/<int:cv_id>/download')
@login_required
def download_cv(cv_id):
    """Tải xuống CV (hỗ trợ cả PDF và PNG)"""
    format_type = request.args.get('format', 'pdf').lower()
    dpi = int(request.args.get('dpi', 300))
    
    try:
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            flash('Không tìm thấy CV.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Lấy content của CV
        content = cv.get_content()
        template_data = content.get('template_data', {})
        
        if not template_data:
            flash('CV không có dữ liệu template để xuất.', 'error')
            return redirect(url_for('cv.cv_preview', cv_id=cv_id))
        
        # Tạo tên file an toàn
        safe_title = "".join(c for c in cv.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format_type == 'png':
            # Tạo file tạm thời để lưu PNG
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_png_file:
                temp_png_path = tmp_png_file.name
            
            try:
                # Khởi tạo converter và tạo PNG
                converter = KonvaJSONToPDF(dpi=72)
                converter.convert_json_to_png(template_data, temp_png_path, pdf_path=None, delete_pdf=True, png_dpi=dpi)
                
                # Tăng số lượt tải xuống
                cv.increment_downloads()
                
                # Tạo tên file PNG
                png_filename = f"{safe_title}_{cv_id}.png"
                
                # Trả về file PNG
                response = send_file(
                    temp_png_path,
                    as_attachment=True,
                    download_name=png_filename,
                    mimetype='image/png'
                )
                
                # Xóa file tạm sau khi gửi
                response.call_on_close(lambda: os.unlink(temp_png_path) if os.path.exists(temp_png_path) else None)
                
                return response
                
            except Exception as e:
                # Xóa file tạm nếu có lỗi
                if os.path.exists(temp_png_path):
                    os.unlink(temp_png_path)
                raise e
        else:  # format_type == 'pdf' (default)
            # Redirect to PDF export
            return redirect(url_for('cv.export_cv_pdf', cv_id=cv_id))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi tải xuống CV: {str(e)}', 'error')
        return redirect(url_for('cv.cv_preview', cv_id=cv_id))

@cv_bp.route('/<int:cv_id>/export-pdf')
@login_required
def export_cv_pdf(cv_id):
    """Xuất CV ra file PDF"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            flash('Không tìm thấy CV hoặc bạn không có quyền truy cập.', 'error')
            return redirect(url_for('cv.cv_list'))
        
        # Lấy content của CV
        content = cv.get_content()
        template_data = content.get('template_data', {})
        
        if not template_data:
            flash('CV không có dữ liệu template để xuất PDF.', 'error')
            return redirect(url_for('cv.cv_preview', cv_id=cv_id))
        
        # Tạo file tạm thời để lưu PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            temp_pdf_path = tmp_file.name
        
        try:
            # Khởi tạo converter và tạo PDF
            converter = KonvaJSONToPDF(dpi=72)
            converter.convert_json_to_pdf(template_data, temp_pdf_path)
            
            # Tăng số lượt tải xuống
            cv.increment_downloads()
            
            # Tạo tên file PDF
            safe_title = "".join(c for c in cv.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            pdf_filename = f"{safe_title}_{cv.id}.pdf"
            
            # Trả về file PDF
            def remove_file(response):
                try:
                    os.unlink(temp_pdf_path)
                except Exception:
                    pass
                return response
            
            response = send_file(
                temp_pdf_path,
                as_attachment=True,
                download_name=pdf_filename,
                mimetype='application/pdf'
            )
            
            # Xóa file tạm sau khi gửi
            response.call_on_close(lambda: os.unlink(temp_pdf_path) if os.path.exists(temp_pdf_path) else None)
            
            return response
            
        except Exception as e:
            # Xóa file tạm nếu có lỗi
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            raise e
            
    except Exception as e:
        print(f"Error exporting PDF: {str(e)}")
        flash(f'Có lỗi xảy ra khi xuất PDF: {str(e)}', 'error')
        return redirect(url_for('cv.cv_preview', cv_id=cv_id))

@cv_bp.route('/api/<int:cv_id>/export-pdf', methods=['POST'])
@login_required
def api_export_cv_pdf(cv_id):
    """API endpoint để xuất CV ra PDF (AJAX)"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy CV hoặc bạn không có quyền truy cập.'
            })
        
        # Kiểm tra template_data
        content = cv.get_content()
        template_data = content.get('template_data', {})
        
        if not template_data:
            return jsonify({
                'success': False,
                'error': 'CV không có dữ liệu template để xuất PDF.'
            })
        
        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            temp_pdf_path = tmp_file.name
        
        try:
            # Tạo PDF
            converter = KonvaJSONToPDF(dpi=72)
            converter.convert_json_to_pdf(template_data, temp_pdf_path)
            
            # Tăng download count
            cv.increment_downloads()
            
            # Tạo download URL
            download_url = url_for('cv.export_cv_pdf', cv_id=cv_id)
            
            return jsonify({
                'success': True,
                'message': 'PDF đã được tạo thành công!',
                'download_url': download_url,
                'filename': f"{cv.title}_{cv_id}.pdf"
            })
            
        except Exception as e:
            # Cleanup temp file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            
            return jsonify({
                'success': False,
                'error': f'Lỗi khi tạo PDF: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Có lỗi xảy ra: {str(e)}'
        })

# API endpoints for AJAX calls
@cv_bp.route('/api/validate-section', methods=['POST'])
@login_required
def validate_section():
    """Validate form section"""
    section = request.json.get('section')
    data = request.json.get('data')
    
    errors = []
    
    if section == 'personal':
        if not data.get('full_name'):
            errors.append('Họ tên là bắt buộc')
        if not data.get('email'):
            errors.append('Email là bắt buộc')
        elif not is_valid_email(data.get('email')):
            errors.append('Email không hợp lệ')
        if not data.get('position'):
            errors.append('Vị trí ứng tuyển là bắt buộc')
    
    elif section == 'education':
        if not data.get('education_school'):
            errors.append('Thông tin trường học là bắt buộc')
        if not data.get('education_degree'):
            errors.append('Thông tin chuyên ngành là bắt buộc')
    
    elif section == 'experience':
        if not data.get('experience_company'):
            errors.append('Thông tin công ty là bắt buộc')
        if not data.get('experience_position'):
            errors.append('Thông tin vị trí làm việc là bắt buộc')
    
    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors
    })

@cv_bp.route('/api/auto-suggest', methods=['POST'])
@login_required
def auto_suggest():
    """Auto suggest content using AI"""
    field = request.json.get('field')
    context = request.json.get('context', {})
    
    # TODO: Implement Gemini AI suggestions
    suggestions = {
        'summary': [
            'Chuyên gia phát triển phần mềm với kinh nghiệm vững chắc trong xây dựng ứng dụng web và mobile.',
            'Lập trình viên đam mê công nghệ với khả năng học hỏi nhanh và kỹ năng giải quyết vấn đề hiệu quả.',
            'Developer có kinh nghiệm làm việc với các công nghệ hiện đại và tinh thần teamwork cao.'
        ],
        'skills': ['React.js', 'Vue.js', 'Node.js', 'Python', 'JavaScript', 'TypeScript', 'Django', 'Flask'],
        'experience_description': [
            '• Phát triển và duy trì các ứng dụng web sử dụng React.js và Node.js\n• Tối ưu hiệu suất ứng dụng, giảm thời gian tải trang xuống 40%\n• Hợp tác với team design để tạo ra giao diện người dùng trực quan',
            '• Xây dựng API RESTful và tích hợp với cơ sở dữ liệu MongoDB\n• Triển khai CI/CD pipeline sử dụng Docker và Jenkins\n• Mentor cho junior developers và review code'
        ]
    }
    
    return jsonify({
        'suggestions': suggestions.get(field, [])
    })


@cv_bp.route('/bulk-action', methods=['POST'])
@login_required
def bulk_action():
    """Thực hiện hành động hàng loạt trên CV"""
    try:
        data = request.get_json()
        action = data.get('action')
        cv_ids = data.get('cv_ids', [])
        
        if not cv_ids:
            return jsonify({'success': False, 'error': 'Không có CV nào được chọn.'})
        
        # Lấy các CV thuộc về user hiện tại
        cvs = CV.query.filter(CV.id.in_(cv_ids), CV.user_id == current_user.id).all()
        
        if not cvs:
            return jsonify({'success': False, 'error': 'Không tìm thấy CV nào hợp lệ.'})
        
        success_count = 0
        
        if action == 'delete':
            for cv in cvs:
                db.session.delete(cv)
                success_count += 1
                
        elif action == 'duplicate':
            for cv in cvs:
                new_cv = CV(
                    title=f"Bản sao - {cv.title}",
                    content=cv.content,
                    template_id=cv.template_id,
                    user_id=current_user.id
                )
                db.session.add(new_cv)
                success_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã thực hiện thành công trên {success_count} CV.',
            'affected_count': success_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Có lỗi xảy ra khi thực hiện hành động.'})

# Thêm Canvas Editor Endpoint để test giao diện
@cv_bp.route('/canvas-editor')
@cv_bp.route('/canvas-editor/<int:cv_id>')
@login_required
def canvas_editor(cv_id=None):
    """Canvas Editor - Giao diện thiết kế CV với drag & drop"""
    try:
        cv_data = None
        template_data = {}
        
        # 1. Lấy CV nếu có cv_id
        if cv_id:
            # Lấy CV từ database
            cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
            
            if not cv:
                flash('Không tìm thấy CV hoặc bạn không có quyền truy cập.', 'error')
                return redirect(url_for('cv.cv_list'))
            
            # Lấy dữ liệu từ CV
            content = cv.get_content()
            template_data = content.get('template_data', {})
            
            # Chuẩn bị dữ liệu CV cho canvas
            cv_data = {
                'id': cv.id,
                'title': cv.title,
                'template_id': cv.template_id,
                'template_data': template_data,
                'created_at': cv.created_at.isoformat() if cv.created_at else None,
                'updated_at': cv.updated_at.isoformat() if cv.updated_at else None
            }
            
            # Tăng lượt xem
            cv.increment_views()
            
        else:
            # Không có cv_id - tạo canvas trống
            cv_data = {
                'id': None,
                'title': 'CV Mới',
                'template_id': 'modern',
                'template_data': {},
                'created_at': None,
                'updated_at': None
            }
        
        # Đảm bảo template_data có thể serialize thành JSON
        try:
            import json
            json.dumps(template_data)
        except (TypeError, ValueError):
            # Nếu template_data không thể serialize, tạo object rỗng
            template_data = {}
            if cv_data:
                cv_data['template_data'] = {}
        
        # Lấy danh sách templates có sẵn cho selector
        available_templates = CVTemplate.query.filter(CVTemplate.is_active == True).all()
        
        return render_template('cv/canvas_editor.html', 
                             cv=cv_data,
                             template_data=json.dumps(template_data) if template_data else '{}',
                             available_templates=available_templates,
                             edit_mode=cv_id is not None)
        
    except Exception as e:
        print(f"Error in canvas_editor: {str(e)}")
        import traceback
        traceback.print_exc()
        
        flash('Có lỗi xảy ra khi tải Canvas Editor. Vui lòng thử lại.', 'error')
        return redirect(url_for('cv.cv_list'))

@cv_bp.route('/save-form', methods=['POST'])
@login_required
def save_cv_form():
    try:
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # lấy dữ liệu từ form
        form_data = request.form.to_dict(flat=False)
        
        # Reformat single-item lists to strings for simple fields
        for key, value in form_data.items():
            if isinstance(value, list) and len(value) == 1 and not key.endswith('[]'):
                form_data[key] = value[0]
        
        # validate dữ liệu
        errors = validate_cv_data(form_data)
        if errors:
            if is_ajax:
                return jsonify({'success': False, 'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('cv.create_cv'))
        
        # Lấy template_id
        template_id = form_data.get('template_id', 'modern_complete')
        
        # Lấy template mặc định từ cv_template
        template = CVTemplate.query.get(template_id)
        if not template:
            # Fallback to default template
            CVTemplate.seed_default_templates()
            template = CVTemplate.query.get('modern_complete')
            if not template:
                return jsonify({'success': False, 'errors': ['Template không tồn tại']}), 400
        
        # tạo cv mới
        new_cv = CV(
            title=form_data.get('title', f"CV {form_data.get('position', 'mới')}"),
            user_id=current_user.id,
            template_id=template_id
        )
        
        # thay thế dữ liệu từ form vào template
        template_data = template.get_template_data()
        
        # Chuẩn bị dữ liệu để replace với structured data
        replacement_data = {
            'full_name': form_data.get('full_name', ''),
            'position': form_data.get('position', ''),
            'email': form_data.get('email', ''),
            'phone': form_data.get('phone', ''),
            'address': form_data.get('address', ''),
            'website': form_data.get('website', ''),
            'summary': form_data.get('summary', ''),
            'experience': build_experience_data(form_data),
            'education': build_education_data(form_data),
            'technical_skills': form_data.get('technical_skills[]', []),
            'soft_skills': form_data.get('soft_skills[]', []),
            'languages': form_data.get('languages[]', [])
        }
        
        # Replace template placeholders với dữ liệu thực tế
        processed_template = replace_template_placeholders(template_data, replacement_data)
        
        # set content cho cv (lưu cả template data và form data)
        cv_content = {
            'template_data': processed_template,
            'form_data': replacement_data
        }
        new_cv.set_content(cv_content)
        
        # lưu cv vào database
        db.session.add(new_cv)
        db.session.commit()
        
        # Track template usage
        template.increment_usage()
        
        success_msg = 'CV đã được tạo thành công!'
        redirect_url = url_for('cv.cv_preview', cv_id=new_cv.id)
        
        if is_ajax:
            return jsonify({
                'success': True,
                'message': success_msg,
                'cv': {
                    'id': new_cv.id,
                    'title': new_cv.title,
                    'template_id': new_cv.template_id,
                    'created_at': new_cv.created_at.isoformat()
                },
                'redirect_url': redirect_url
            })
        
        flash(success_msg, 'success')
        return redirect(redirect_url)
        
    except Exception as e:
        db.session.rollback()
        error_msg = f'Có lỗi xảy ra khi tạo CV: {str(e)}'
        
        if is_ajax:
            return jsonify({'success': False, 'errors': [error_msg]}), 500
        
        flash(error_msg, 'error')
        return redirect(url_for('cv.create_cv'))

@cv_bp.route('/save-canvas', methods=['POST'])
@login_required
def save_cv_canvas():
    """Lưu CV từ Canvas Editor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ.'}), 400

        cv_id = data.get('cv_id')
        title = data.get('title', 'CV Mới từ Canvas')
        template_id_from_request = data.get('template_id')
        template_data_json = data.get('template_data_json')

        if not template_data_json:
            return jsonify({'success': False, 'error': 'Không có dữ liệu canvas để lưu.'}), 400

        try:
            template_data = json.loads(template_data_json)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Dữ liệu canvas không hợp lệ (JSON format).'}), 400

        saved_cv = None

        if cv_id:
            # Cập nhật CV hiện có
            cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
            if not cv:
                return jsonify({'success': False, 'error': 'Không tìm thấy CV hoặc bạn không có quyền truy cập.'}), 404
            
            cv.title = title
            # Giữ lại form_data nếu có, chỉ cập nhật template_data
            current_content = cv.get_content()
            if not isinstance(current_content, dict): # Khởi tạo nếu content không phải dict
                current_content = {}
            current_content['template_data'] = template_data
            cv.set_content(current_content)
            
            cv.is_canvas_editor = True
            cv.updated_at = datetime.utcnow()
            saved_cv = cv
        else:
            # Tạo CV mới
            new_cv = CV(
                user_id=current_user.id,
                title=title,
                template_id=template_id_from_request or 'default_canvas' # Sử dụng template_id từ request hoặc mặc định
            )
            # Với CV mới từ canvas, form_data có thể khởi tạo rỗng
            new_cv.set_content({'template_data': template_data, 'form_data': {}})
            new_cv.is_canvas_editor = True
            
            db.session.add(new_cv)
            db.session.flush() # Flush để lấy new_cv.id trước khi commit
            saved_cv = new_cv

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'CV đã được lưu thành công!',
            'cv_id': saved_cv.id,
            'title': saved_cv.title,
            'updated_at': saved_cv.updated_at.isoformat(),
            'redirect_url': url_for('cv.canvas_editor', cv_id=saved_cv.id)
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving canvas CV: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Có lỗi xảy ra khi lưu CV: {str(e)}'}), 500
    

@cv_bp.route('api/analyze-cv/<int:cv_id>', methods=['POST'])
@login_required
def analyze_cv(cv_id):
    """Phân tích CV và trả về gợi ý cải thiện"""
    try:
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy CV hoặc bạn không có quyền truy cập.'
            }), 404
        
        # Lấy content để phân tích
        content = cv.get_content()
        
        # Sử dụng GeminiAI để đánh giá CV
        ai_evaluation = ai.evaluate_cv(content)
        
        # Lấy kết quả từ AI evaluation
        overall_score = ai_evaluation.get('overall_score', 0)
        section_scores = ai_evaluation.get('section_scores', {})
        ai_suggestions = ai_evaluation.get('suggestions', [])
        # Map section scores từ AI response
        personal_info_score = section_scores.get('personal_info', 0)
        experience_score = section_scores.get('work_experience', 0)
        skills_score = section_scores.get('skills', 0)
        education_score = section_scores.get('education', 0)
        
        # Tạo gợi ý cải thiện từ AI suggestions và scores
        suggestions = generate_improvement_suggestions_from_ai(ai_suggestions, section_scores, overall_score)
        
        return jsonify({
            'success': True,
            'analysis': {
                'overall_score': round(overall_score, 1),
                'personal_info_score': round(personal_info_score, 1),
                'experience_score': round(experience_score, 1),
                'skills_score': round(skills_score, 1),
                'education_score': round(education_score, 1),
                'ai_feedback': f'AI đánh giá tổng thể: {overall_score}/100 điểm',
                'strengths': extract_strengths_from_scores(section_scores),
                'weaknesses': extract_weaknesses_from_scores(section_scores)
            },
            'suggestions': suggestions
        })
        
    except Exception as e:
        print(f"Error analyzing CV: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Có lỗi xảy ra khi phân tích CV. Vui lòng thử lại.'
        }), 500

def generate_improvement_suggestions_from_ai(ai_suggestions, section_scores, overall_score):
    """Tạo gợi ý cải thiện từ kết quả AI và điểm số các phần"""
    suggestions = []
    
    # Thêm gợi ý từ AI
    for suggestion_text in ai_suggestions:
        # Xác định loại gợi ý dựa trên nội dung
        suggestion_type = 'info'
        icon = 'fas fa-lightbulb'
        
        if any(keyword in suggestion_text.lower() for keyword in ['thiếu', 'không có', 'cần bổ sung', 'chưa có']):
            suggestion_type = 'warning'
            icon = 'fas fa-exclamation-triangle'
        elif any(keyword in suggestion_text.lower() for keyword in ['tốt', 'xuất sắc', 'hoàn thiện', 'chất lượng']):
            suggestion_type = 'success'
            icon = 'fas fa-check-circle'
        
        suggestions.append({
            'type': suggestion_type,
            'icon': icon,
            'title': 'Gợi ý từ AI',
            'description': suggestion_text
        })
    
    # Thêm gợi ý dựa trên điểm số các phần
    if section_scores.get('personal_info', 0) < 60:
        suggestions.append({
            'type': 'warning',
            'icon': 'fas fa-user',
            'title': 'Cải thiện thông tin cá nhân',
            'description': 'Bổ sung đầy đủ thông tin liên hệ, tóm tắt bản thân và mục tiêu nghề nghiệp.'
        })
    
    if section_scores.get('work_experience', 0) < 60:
        suggestions.append({
            'type': 'warning',
            'icon': 'fas fa-briefcase',
            'title': 'Mở rộng kinh nghiệm làm việc',
            'description': 'Mô tả chi tiết hơn về trách nhiệm, thành tích và kết quả đạt được trong các vị trí đã làm.'
        })
    
    if section_scores.get('skills', 0) < 60:
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-tools',
            'title': 'Bổ sung kỹ năng',
            'description': 'Thêm các kỹ năng kỹ thuật và kỹ năng mềm liên quan đến vị trí ứng tuyển.'
        })
    
    if section_scores.get('education', 0) < 60:
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-graduation-cap',
            'title': 'Hoàn thiện thông tin học vấn',
            'description': 'Bổ sung thông tin về bằng cấp, chứng chỉ và các khóa học liên quan.'
        })
    
    if section_scores.get('presentation', 0) < 60:
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-palette',
            'title': 'Cải thiện cách trình bày',
            'description': 'Tối ưu hóa bố cục, phông chữ và cách sắp xếp thông tin để CV dễ đọc hơn.'
        })
    
    # Gợi ý tích cực nếu điểm cao
    if overall_score >= 80:
        suggestions.append({
            'type': 'success',
            'icon': 'fas fa-star',
            'title': 'CV chất lượng cao!',
            'description': 'CV của bạn đã đạt tiêu chuẩn tốt và sẵn sàng để ứng tuyển các vị trí mong muốn.'
        })
    
    return suggestions

def extract_strengths_from_scores(section_scores):
    """Trích xuất điểm mạnh từ điểm số các phần"""
    strengths = []
    
    for section, score in section_scores.items():
        if score >= 80:
            section_name = {
                'personal_info': 'Thông tin cá nhân',
                'work_experience': 'Kinh nghiệm làm việc',
                'education': 'Học vấn',
                'skills': 'Kỹ năng',
                'presentation': 'Cách trình bày'
            }.get(section, section)
            
            strengths.append(f"{section_name} đã hoàn thiện tốt")
    
    return strengths if strengths else ["CV có bố cục cơ bản"]

def extract_weaknesses_from_scores(section_scores):
    """Trích xuất điểm yếu từ điểm số các phần"""
    weaknesses = []
    
    for section, score in section_scores.items():
        if score < 60:
            section_name = {
                'personal_info': 'Thông tin cá nhân',
                'work_experience': 'Kinh nghiệm làm việc', 
                'education': 'Học vấn',
                'skills': 'Kỹ năng',
                'presentation': 'Cách trình bày'
            }.get(section, section)
            
            weaknesses.append(f"{section_name} cần được cải thiện")
    
    return weaknesses if weaknesses else ["Không có điểm yếu đặc biệt"]

# Remove the old calculation functions as they are replaced by AI evaluation
# def calculate_personal_info_score(form_data):
# def calculate_experience_score(form_data):
# def calculate_skills_score(form_data):
# def calculate_education_score(form_data):
# def generate_improvement_suggestions(form_data, scores):

@cv_bp.route('/api/ai-hint', methods=['POST'])
@login_required
def ai_hint():
    """Gợi ý nội dung CV bằng AI (Gemini)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ.'}), 400

        user_message = data.get('user_message')
        context = data.get('context', {})
        element_type = context.get('type', 'không rõ') # e.g., 'summary', 'experience_description'
        current_content = context.get('content', '')

        if not user_message:
            return jsonify({'success': False, 'error': 'Thiếu thông điệp người dùng (user_message).'}), 400

        # Construct a more detailed prompt for the AI
        prompt = f"""
Người dùng đang soạn thảo CV và cần một gợi ý.
Loại mục đang chỉnh sửa: "{element_type}"
Nội dung hiện tại của mục đó: "{current_content}"
Yêu cầu của người dùng: "{user_message}"

Dựa vào thông tin trên, hãy đưa ra một gợi ý ngắn gọn, tập trung và hữu ích để cải thiện nội dung cho mục "{element_type}".
Nếu nội dung hiện tại trống, hãy đưa ra một gợi ý khởi đầu.
Nếu yêu cầu của người dùng là viết lại, hãy viết lại nội dung hiện tại theo hướng tốt hơn.
Nếu yêu cầu là ý tưởng, hãy cung cấp một vài ý tưởng.
Chỉ trả về phần gợi ý/nội dung được tạo ra, không thêm lời chào hay giải thích.
"""

        suggestion = ai.generate_text(prompt)

        if suggestion:
            return jsonify({'success': True, 'suggestion': suggestion.strip()})
        else:
            return jsonify({'success': False, 'error': 'Không thể tạo gợi ý từ AI. Vui lòng thử lại.'}), 500

    except Exception as e:
        print(f"Error in AI hint: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Có lỗi xảy ra: {str(e)}'}), 500
    
@cv_bp.route('/api/translate-cv/<int:cv_id>', methods=['POST'])
@login_required
def translate_cv(cv_id):
    """Dịch nội dung CV sang ngôn ngữ khác bằng AI (Gemini)"""
    try:
        data = request.get_json()
        target_language = data.get('target_language', 'vi') if data else 'vi'
        
        # Lấy CV từ database
        cv = CV.query.filter_by(id=cv_id, user_id=current_user.id).first()
        
        if not cv:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy CV hoặc bạn không có quyền truy cập.'
            }), 404
        
        # Lấy content của CV
        content = cv.get_content()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'CV không có nội dung để dịch.'
            }), 400
        
        # Sử dụng GeminiAI để dịch nội dung CV
        translated_content = ai.translate_text(content, target_language)
        
        # Mapping ngôn ngữ để tạo title
        language_names = {
            'vi': 'Tiếng Việt',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'es': 'Español',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文'
        }
        
        target_lang_name = language_names.get(target_language, target_language.upper())
        
        # Tạo CV mới với nội dung đã dịch
        new_cv = CV(
            title=f"CV - {target_lang_name} - {cv.title}",
            content=cv.content,  # Sẽ được cập nhật bên dưới
            template_id=cv.template_id,
            user_id=current_user.id,
            is_canvas_editor=cv.is_canvas_editor
        )
        
        # Cập nhật content với nội dung đã dịch
        new_cv.set_content(translated_content)
        
        # Lưu CV mới vào database
        db.session.add(new_cv)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'CV đã được dịch sang {target_lang_name} thành công!',
            'new_cv': {
                'id': new_cv.id,
                'title': new_cv.title,
                'template_id': new_cv.template_id,
                'created_at': new_cv.created_at.isoformat(),
                'is_canvas_editor': True
            },
            'redirect_url': url_for('cv.cv_preview', cv_id=new_cv.id)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error translating CV: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Có lỗi xảy ra khi dịch CV: {str(e)}'
        }), 500