from datetime import datetime
from typing import Dict, List, Any, Optional
import copy
import re


class CVDataUpdater:
    """Class để cập nhật dữ liệu CV từ form input"""
    
    def __init__(self):
        # Mapping giữa form fields và template element IDs
        self.field_mappings = {
            'full_name': {'id': 'full_name', 'key': 'text'},
            'position': {'id': 'position', 'key': 'text'},
            'email': {'id': 'email', 'key': 'text'},
            'phone': {'id': 'phone', 'key': 'text'},
            'address': {'id': 'address', 'key': 'text'},
            'summary': {'id': 'summary', 'key': 'text'},
        }
    
    def find_element_by_id(self, data: Dict, target_id: str) -> Optional[Dict]:
        """Tìm element theo ID trong template data"""
        def search_in_children(children: List) -> Optional[Dict]:
            for child in children:
                if child.get('attrs', {}).get('id') == target_id:
                    return child
                if 'children' in child:
                    found = search_in_children(child['children'])
                    if found:
                        return found
            return None
        
        template_data = data.get('template_data', {})
        children = template_data.get('children', [])
        return search_in_children(children)
    
    def update_cv_data(self, cv_data: Dict, form_updates: Dict) -> Dict:
        """Cập nhật cả form_data và template_data dựa trên form input"""
        # Deep copy để tránh mutation của object gốc
        updated_data = copy.deepcopy(cv_data)
        
        # Cập nhật form_data
        form_data = updated_data.get('form_data', {})
        for key, value in form_updates.items():
            form_data[key] = value
        updated_data['form_data'] = form_data
        
        # Cập nhật template_data dựa trên form_data mới
        self._update_template_from_form_data(updated_data)
        
        return updated_data
    
    def _update_template_from_form_data(self, data: Dict) -> None:
        """Cập nhật template_data dựa trên form_data"""
        form_data = data.get('form_data', {})
        
        # Cập nhật các field đơn giản
        self._update_simple_fields(data, form_data)
        
        # Cập nhật các sections phức tạp
        self._update_experience_section(data, form_data)
        self._update_education_section(data, form_data)
        self._update_skills_section(data, form_data)
        self._update_languages_section(data, form_data)
    
    def _update_simple_fields(self, data: Dict, form_data: Dict) -> None:
        """Cập nhật các field đơn giản"""
        # Cập nhật các field đơn giản
        simple_fields = ['full_name', 'position', 'summary']
        for field in simple_fields:
            if field in form_data and form_data[field]:
                element = self.find_element_by_id(data, field)
                if element and 'attrs' in element:
                    element['attrs']['text'] = form_data[field]
        
        # Cập nhật email với icon
        if 'email' in form_data and form_data['email']:
            element = self.find_element_by_id(data, 'email')
            if element and 'attrs' in element:
                element['attrs']['text'] = f"✉ {form_data['email']}"
        
        # Cập nhật phone với icon
        if 'phone' in form_data and form_data['phone']:
            element = self.find_element_by_id(data, 'phone')
            if element and 'attrs' in element:
                element['attrs']['text'] = f"📞 {form_data['phone']}"
        
        # Cập nhật address với icon
        if 'address' in form_data and form_data['address']:
            element = self.find_element_by_id(data, 'address')
            if element and 'attrs' in element:
                element['attrs']['text'] = f"📍 {form_data['address']}"
    
    def _update_experience_section(self, data: Dict, form_data: Dict) -> None:
        """Cập nhật section kinh nghiệm làm việc"""
        experiences = form_data.get('experience', [])
        
        for i, exp in enumerate(experiences):
            if not exp:
                continue
                
            exp_num = i + 1
            
            # Cập nhật position
            if exp.get('position'):
                element = self.find_element_by_id(data, f'exp{exp_num}_position')
                if element and 'attrs' in element:
                    element['attrs']['text'] = exp['position']
            
            # Cập nhật company
            if exp.get('company'):
                element = self.find_element_by_id(data, f'exp{exp_num}_company')
                if element and 'attrs' in element:
                    element['attrs']['text'] = exp['company']
            
            # Cập nhật date range
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            if start_date or end_date:
                element = self.find_element_by_id(data, f'exp{exp_num}_date')
                if element and 'attrs' in element:
                    element['attrs']['text'] = f"{start_date} - {end_date}".strip(' -')
            
            # Cập nhật description
            if exp.get('description'):
                element = self.find_element_by_id(data, f'exp{exp_num}_description')
                if element and 'attrs' in element:
                    element['attrs']['text'] = exp['description']
    
    def _update_education_section(self, data: Dict, form_data: Dict) -> None:
        """Cập nhật section học vấn"""
        educations = form_data.get('education', [])
        
        for i, edu in enumerate(educations):
            if not edu:
                continue
                
            edu_num = i + 1
            
            # Cập nhật degree
            if edu.get('degree'):
                element = self.find_element_by_id(data, f'edu{edu_num}_degree')
                if element and 'attrs' in element:
                    element['attrs']['text'] = edu['degree']
            
            # Cập nhật school
            if edu.get('school'):
                element = self.find_element_by_id(data, f'edu{edu_num}_school')
                if element and 'attrs' in element:
                    element['attrs']['text'] = edu['school']
            
            # Cập nhật date range
            start_date = edu.get('start_date', '')
            end_date = edu.get('end_date', '')
            if start_date or end_date:
                element = self.find_element_by_id(data, f'edu{edu_num}_date')
                if element and 'attrs' in element:
                    element['attrs']['text'] = f"{start_date} - {end_date}".strip(' -')
            
            # Cập nhật description
            if edu.get('description'):
                element = self.find_element_by_id(data, f'edu{edu_num}_description')
                if element and 'attrs' in element:
                    element['attrs']['text'] = edu['description']
    
    def _update_skills_section(self, data: Dict, form_data: Dict) -> None:
        """Cập nhật section kỹ năng"""
        # Technical skills
        technical_skills = form_data.get('technical_skills', [])
        if technical_skills:
            # Cập nhật danh sách tổng hợp
            element = (self.find_element_by_id(data, 'tech_skills_list') or 
                      self.find_element_by_id(data, 'technical_skills'))
            if element and 'attrs' in element:
                element['attrs']['text'] = ', '.join(technical_skills)
            
            # Cập nhật từng skill riêng lẻ
            for i, skill in enumerate(technical_skills[:5]):  # Giới hạn 5 skills
                skill_num = i + 1
                element = self.find_element_by_id(data, f'tech_skill_{skill_num}')
                if element and 'attrs' in element:
                    element['attrs']['text'] = skill
        
        # Soft skills
        soft_skills = form_data.get('soft_skills', [])
        if soft_skills:
            # Cập nhật danh sách tổng hợp
            element = (self.find_element_by_id(data, 'soft_skills_list') or 
                      self.find_element_by_id(data, 'soft_skills'))
            if element and 'attrs' in element:
                element['attrs']['text'] = ', '.join(soft_skills)
            
            # Cập nhật từng skill riêng lẻ
            for i, skill in enumerate(soft_skills[:5]):  # Giới hạn 5 skills
                skill_num = i + 1
                element = self.find_element_by_id(data, f'soft_skill_{skill_num}')
                if element and 'attrs' in element:
                    element['attrs']['text'] = skill
    
    def _update_languages_section(self, data: Dict, form_data: Dict) -> None:
        """Cập nhật section ngôn ngữ"""
        languages = form_data.get('languages', [])
        if languages:
            # Cập nhật danh sách tổng hợp
            element = self.find_element_by_id(data, 'languages_list')
            if element and 'attrs' in element:
                element['attrs']['text'] = ', '.join(languages)
            
            # Cập nhật từng ngôn ngữ riêng lẻ
            for i, lang in enumerate(languages[:5]):  # Giới hạn 5 ngôn ngữ
                lang_num = i + 1
                element = self.find_element_by_id(data, f'language_{lang_num}')
                if element and 'attrs' in element:
                    element['attrs']['text'] = lang


# Data extraction and formatting functions
def extract_form_data(form):
    """Trích xuất dữ liệu từ form"""
    return {
        'title': form.get('title', ''),
        'full_name': form.get('full_name', ''),
        'position': form.get('position', ''),
        'email': form.get('email', ''),
        'phone': form.get('phone', ''),
        'address': form.get('address', ''),
        'website': form.get('website', ''),
        'summary': form.get('summary', ''),
        # Education arrays
        'education_school': form.getlist('education_school[]'),
        'education_degree': form.getlist('education_degree[]'),
        'education_start': form.getlist('education_start[]'),
        'education_end': form.getlist('education_end[]'),
        'education_description': form.getlist('education_description[]'),
        # Experience arrays
        'experience_company': form.getlist('experience_company[]'),
        'experience_position': form.getlist('experience_position[]'),
        'experience_start': form.getlist('experience_start[]'),
        'experience_end': form.getlist('experience_end[]'),
        'experience_description': form.getlist('experience_description[]'),
        # Skills arrays
        'technical_skills': form.getlist('technical_skills[]'),
        'technical_level': form.getlist('technical_level[]'),
        'soft_skills': form.getlist('soft_skills[]'),
        'soft_level': form.getlist('soft_level[]'),
        'languages': form.getlist('languages[]'),
        'language_level': form.getlist('language_level[]'),
    }


def validate_cv_data(data):
    """Validate CV data"""
    errors = []
    
    if not data.get('full_name'):
        errors.append('Họ tên là bắt buộc.')
    
    if not data.get('email'):
        errors.append('Email là bắt buộc.')
    elif not is_valid_email(data.get('email')):
        errors.append('Email không hợp lệ.')
    
    if not data.get('position'):
        errors.append('Vị trí ứng tuyển là bắt buộc.')
    
    return errors


def is_valid_email(email):
    """Kiểm tra email hợp lệ"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None


def format_time_ago(dt):
    """Format thời gian dạng 'x ngày trước'"""
    if not dt:
        return 'Không xác định'
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return '1 ngày trước'
        elif diff.days < 7:
            return f'{diff.days} ngày trước'
        elif diff.days < 30:
            weeks = diff.days // 7
            return f'{weeks} tuần trước'
        else:
            months = diff.days // 30
            return f'{months} tháng trước'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} giờ trước'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} phút trước'
    else:
        return 'Vừa xong'


def get_cv_statistics(cv_model, user_id):
    """Lấy thống kê CV của user"""
    cvs = cv_model.query.filter_by(user_id=user_id).all()
    
    total_downloads = 0  # TODO: Implement download tracking
    
    stats = {
        'total_cvs': len(cvs),
        'total': len(cvs),  # Keep both for compatibility
        'total_views': sum(cv.views for cv in cvs),
        'total_downloads': total_downloads
    }
    
    return stats


def search_cvs(cv_model, query, user_id):
    """Tìm kiếm CV theo từ khóa"""
    if not query:
        return cv_model.query.filter_by(user_id=user_id).order_by(cv_model.updated_at.desc()).all()
    
    # Tìm kiếm theo title hoặc trong content
    cvs = cv_model.query.filter_by(user_id=user_id).all()
    results = []
    
    query_lower = query.lower()
    
    for cv in cvs:
        # Tìm trong title
        if query_lower in cv.title.lower():
            results.append(cv)
            continue
            
        # Tìm trong content
        content = cv.get_content()
        search_fields = [
            content.get('full_name', ''),
            content.get('position', ''),
            content.get('summary', ''),
        ]
        
        # Thêm education và experience vào tìm kiếm
        for edu in content.get('education', []):
            search_fields.extend([edu.get('school', ''), edu.get('degree', '')])
            
        for exp in content.get('experience', []):
            search_fields.extend([exp.get('company', ''), exp.get('position', '')])
        
        # Kiểm tra từ khóa trong các trường
        if any(query_lower in field.lower() for field in search_fields if field):
            results.append(cv)
    
    return results


def sort_cvs(cvs, sort_by):
    """Sắp xếp danh sách CV"""
    if sort_by == 'name':
        return sorted(cvs, key=lambda x: x.title.lower())
    elif sort_by == 'views':
        return sorted(cvs, key=lambda x: x.views, reverse=True)
    elif sort_by == 'oldest':
        return sorted(cvs, key=lambda x: x.updated_at)
    else:  # newest (default)
        return sorted(cvs, key=lambda x: x.updated_at, reverse=True)


def generate_cv_suggestions(content, completion_score):
    """Tạo gợi ý cải thiện CV"""
    suggestions = []
    
    # Kiểm tra thông tin cá nhân
    if not content.get('phone'):
        suggestions.append({
            'type': 'warning',
            'icon': 'fas fa-phone',
            'title': 'Thêm số điện thoại',
            'description': 'Thêm số điện thoại để nhà tuyển dụng có thể liên hệ trực tiếp'
        })
    
    if not content.get('address'):
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-map-marker-alt',
            'title': 'Thêm địa chỉ',
            'description': 'Địa chỉ giúp nhà tuyển dụng biết vị trí làm việc phù hợp'
        })
    
    # Kiểm tra mô tả bản thân
    summary = content.get('summary', '')
    if not summary:
        suggestions.append({
            'type': 'warning',
            'icon': 'fas fa-user',
            'title': 'Thêm mô tả bản thân',
            'description': 'Mô tả ngắn gọn về bản thân và mục tiêu nghề nghiệp'
        })
    elif len(summary) < 50:
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-edit',
            'title': 'Mở rộng mô tả',
            'description': 'Mô tả bản thân nên có ít nhất 50 ký tự để tạo ấn tượng tốt'
        })
    
    # Kiểm tra kinh nghiệm
    experience = content.get('experience', [])
    if not experience:
        suggestions.append({
            'type': 'warning',
            'icon': 'fas fa-briefcase',
            'title': 'Thêm kinh nghiệm làm việc',
            'description': 'Thêm ít nhất một kinh nghiệm làm việc hoặc thực tập'
        })
    
    # Kiểm tra kỹ năng
    technical_skills = content.get('technical_skills', [])
    if len(technical_skills) < 3:
        suggestions.append({
            'type': 'info',
            'icon': 'fas fa-code',
            'title': 'Thêm kỹ năng chuyên môn',
            'description': 'Thêm ít nhất 3-5 kỹ năng chuyên môn liên quan đến vị trí ứng tuyển'
        })
    
    return suggestions[:4]  # Giới hạn 4 gợi ý


def build_experience_data(form_data):
    """Xây dựng dữ liệu kinh nghiệm từ form"""
    experience = []
    companies = form_data.get('experience_company[]', [])
    positions = form_data.get('experience_position[]', [])
    start_dates = form_data.get('experience_start[]', [])
    end_dates = form_data.get('experience_end[]', [])  # Sửa ở đây
    descriptions = form_data.get('experience_description[]', [])
    
    for i in range(len(companies)):
        if companies[i]:  # Chỉ thêm nếu có công ty
            experience.append({
                'company': companies[i] if i < len(companies) else '',
                'position': positions[i] if i < len(positions) else '',
                'start_date': start_dates[i] if i < len(start_dates) else '',
                'end_date': end_dates[i] if i < len(end_dates) else '',  # Sửa ở đây
                'description': descriptions[i] if i < len(descriptions) else ''
            })
    
    return experience


def build_education_data(form_data):
    """Xây dựng dữ liệu học vấn từ form"""
    education = []
    schools = form_data.get('education_school[]', [])
    degrees = form_data.get('education_degree[]', [])
    start_dates = form_data.get('education_start[]', [])
    end_dates = form_data.get('education_end[]', [])
    descriptions = form_data.get('education_description[]', [])
    
    for i in range(len(schools)):
        if schools[i]:  # Chỉ thêm nếu có trường học
            education.append({
                'school': schools[i] if i < len(schools) else '',
                'degree': degrees[i] if i < len(degrees) else '',
                'start_date': start_dates[i] if i < len(start_dates) else '',
                'end_date': end_dates[i] if i < len(end_dates) else '',
                'description': descriptions[i] if i < len(descriptions) else ''
            })
    
    return education


def replace_template_placeholders(template_data, replacement_data):
    """Thay thế placeholders trong template với dữ liệu thực tế"""
    # Deep copy template để không modify original
    processed_template = copy.deepcopy(template_data)
    
    def replace_text(text, data):
        """Replace placeholders in text with actual data using regex"""
        if not isinstance(text, str):
            return text
        
        # Replace simple placeholders like {{full_name}}
        def simple_replace(match):
            key = match.group(1)
            return str(data.get(key, '')) if key in data else match.group(0)
        
        text = re.sub(r'\{\{(\w+)\}\}', simple_replace, text)
        
        # Replace array element placeholders like {{experience[0].position}}
        def array_replace(match):
            array_name = match.group(1)
            index = int(match.group(2))
            field = match.group(3)
            
            if array_name in data and isinstance(data[array_name], list):
                if index < len(data[array_name]) and isinstance(data[array_name][index], dict):
                    return str(data[array_name][index].get(field, ''))
            return ''
        
        text = re.sub(r'\{\{(\w+)\[(\d+)\]\.(\w+)\}\}', array_replace, text)
        
        # Replace array item placeholders like {{technical_skills[0]}}
        def array_item_replace(match):
            array_name = match.group(1)
            index = int(match.group(2))
            
            if array_name in data and isinstance(data[array_name], list):
                if index < len(data[array_name]):
                    return str(data[array_name][index])
            return ''
        
        text = re.sub(r'\{\{(\w+)\[(\d+)\]\}\}', array_item_replace, text)
        
        # Handle date ranges like {{experience[0].start_date}} - {{experience[0].end_date}}
        def date_range_replace(match):
            array_name = match.group(1)
            index = int(match.group(2))
            
            if array_name in data and isinstance(data[array_name], list):
                if index < len(data[array_name]) and isinstance(data[array_name][index], dict):
                    item = data[array_name][index]
                    start = item.get('start_date', '')
                    end = item.get('end_date', '')
                    if start or end:
                        return f"{start} - {end}".strip(' -')
            return ''
        
        text = re.sub(r'\{\{(\w+)\[(\d+)\]\.start_date\}\}\s*-\s*\{\{(\w+)\[(\d+)\]\.end_date\}\}', 
                     date_range_replace, text)
        
        return text
    
    # Process all elements in template (new format with nested layers)
    if 'children' in processed_template:
        for layer in processed_template.get('children', []):
            for child in layer.get('children', []):
                if child.get('className') == 'Text' and 'attrs' in child and 'text' in child.get('attrs', {}):
                    child['attrs']['text'] = replace_text(child['attrs']['text'], replacement_data)
    
    return processed_template


def format_skills_for_display(skills_data):
    """Format skills data for template display"""
    if not skills_data:
        return []
    
    formatted_skills = []
    
    # Nếu skills_data là list of strings (old format)
    if isinstance(skills_data, list) and skills_data and isinstance(skills_data[0], str):
        for skill in skills_data:
            formatted_skills.append({
                'name': skill,
                'level': 'Intermediate'  # Default level
            })
    
    # Nếu skills_data là list of dicts (new format)
    elif isinstance(skills_data, list) and skills_data and isinstance(skills_data[0], dict):
        formatted_skills = skills_data
    
    # Nếu skills_data là dict với separate name và level arrays
    elif isinstance(skills_data, dict):
        names = skills_data.get('names', [])
        levels = skills_data.get('levels', [])
        
        for i, name in enumerate(names):
            level = levels[i] if i < len(levels) else 'Intermediate'
            formatted_skills.append({
                'name': name,
                'level': level
            })
    
    return formatted_skills


def format_languages_for_display(languages_data):
    """Format languages data for template display"""
    if not languages_data:
        return []
    
    formatted_languages = []
    
    # Nếu languages_data là list of strings
    if isinstance(languages_data, list) and languages_data and isinstance(languages_data[0], str):
        for lang in languages_data:
            formatted_languages.append({
                'name': lang,
                'level': 'Trung bình'  # Default level
            })
    
    # Nếu languages_data là list of dicts
    elif isinstance(languages_data, list) and languages_data and isinstance(languages_data[0], dict):
        formatted_languages = languages_data
    
    return formatted_languages


def analyze_cv_completeness(cv_data):
    """Analyze CV completeness and return scores"""
    analysis = {
        'overall_score': 0,
        'personal_info_score': 0,
        'experience_score': 0,
        'skills_score': 0,
        'education_score': 0
    }
    
    # Phân tích thông tin cá nhân (25 điểm)
    personal_score = 0
    if cv_data.get('full_name'): personal_score += 5
    if cv_data.get('email'): personal_score += 5
    if cv_data.get('phone'): personal_score += 3
    if cv_data.get('position'): personal_score += 5
    if cv_data.get('address'): personal_score += 2
    if cv_data.get('summary'): personal_score += 5
    analysis['personal_info_score'] = min(100, (personal_score / 25) * 100)
    
    # Phân tích kinh nghiệm (30 điểm)
    experience_score = 0
    experiences = cv_data.get('experience', [])
    if experiences:
        experience_score += 15  # Có kinh nghiệm
        for exp in experiences[:3]:  # Tối đa 3 kinh nghiệm
            if exp.get('company'): experience_score += 2
            if exp.get('position'): experience_score += 2
            if exp.get('description'): experience_score += 1
    analysis['experience_score'] = min(100, (experience_score / 30) * 100)
    
    # Phân tích kỹ năng (25 điểm)
    skills_score = 0
    technical_skills = cv_data.get('technical_skills', [])
    soft_skills = cv_data.get('soft_skills', [])
    
    if technical_skills:
        skills_score += min(15, len(technical_skills) * 3)  # 3 điểm/skill, tối đa 15
    if soft_skills:
        skills_score += min(10, len(soft_skills) * 2)  # 2 điểm/skill, tối đa 10
    
    analysis['skills_score'] = min(100, (skills_score / 25) * 100)
    
    # Phân tích học vấn (20 điểm)
    education_score = 0
    educations = cv_data.get('education', [])
    if educations:
        education_score += 10  # Có học vấn
        for edu in educations[:2]:  # Tối đa 2 học vấn
            if edu.get('school'): education_score += 3
            if edu.get('degree'): education_score += 2
    analysis['education_score'] = min(100, (education_score / 20) * 100)
    
    # Tính điểm tổng thể
    analysis['overall_score'] = int(
        (analysis['personal_info_score'] * 0.25) +
        (analysis['experience_score'] * 0.30) +
        (analysis['skills_score'] * 0.25) +
        (analysis['education_score'] * 0.20)
    )
    
    return analysis


def extract_cv_data_from_template_data(cv, content):
    """Trích xuất dữ liệu CV từ template_data"""
    template_data = content.get('template_data', {})
    
    # Khởi tạo cv_data với thông tin cơ bản
    cv_data = {
        'id': cv.id,
        'title': cv.title,
        'template_id': cv.template_id,
        'template_name': cv.get_template_name(),
        'updated_at': format_time_ago(cv.updated_at),
        'views': cv.views,
        'downloads': getattr(cv, 'downloads', 0),
        
        # Khởi tạo các trường dữ liệu
        'full_name': '',
        'position': '',
        'email': '',
        'phone': '',
        'address': '',
        'website': '',
        'summary': '',
        'experience': [],
        'education': [],
        'technical_skills': [],
        'soft_skills': [],
        'languages': []
    }
    
    # Trích xuất dữ liệu từ template có cấu trúc mới (Konva.js format)
    if 'children' in template_data:
        # Duyệt qua các layer
        for layer in template_data.get('children', []):
            # Duyệt qua các phần tử trong layer
            for element in layer.get('children', []):
                if element.get('className') == 'Text':
                    attrs = element.get('attrs', {})
                    element_id = attrs.get('id', '')
                    text = attrs.get('text', '')
                    
                    # Trích xuất thông tin cá nhân
                    if element_id == 'full_name':
                        cv_data['full_name'] = text
                    elif element_id == 'position':
                        cv_data['position'] = text
                    elif element_id == 'email':
                        # Loại bỏ icon email nếu có
                        cv_data['email'] = text.replace('✉ ', '').replace('✉', '').strip()
                    elif element_id == 'phone':
                        # Loại bỏ icon phone nếu có
                        cv_data['phone'] = text.replace('📞 ', '').replace('📞', '').strip()
                    elif element_id == 'address':
                        # Loại bỏ icon address nếu có
                        cv_data['address'] = text.replace('📍 ', '').replace('📍', '').strip()
                    elif element_id == 'website':
                        cv_data['website'] = text
                    elif element_id == 'summary':
                        cv_data['summary'] = text
                    
                    # Trích xuất kinh nghiệm làm việc
                    elif 'exp' in element_id:
                        extract_experience_from_template(cv_data, element_id, '', text)
                    
                    # Trích xuất học vấn
                    elif 'edu' in element_id:
                        extract_education_from_template(cv_data, element_id, '', text)
    
    # Trích xuất kỹ năng từ form_data nếu template_data không có
    form_data = content.get('form_data', {})
    if not cv_data['technical_skills']:
        cv_data['technical_skills'] = format_skills_for_display(
            form_data.get('technical_skills', [])
        )
    if not cv_data['soft_skills']:
        cv_data['soft_skills'] = format_skills_for_display(
            form_data.get('soft_skills', [])
        )
    if not cv_data['languages']:
        cv_data['languages'] = format_languages_for_display(
            form_data.get('languages', [])
        )
    
    return cv_data


def extract_cv_data_from_form_data(cv, content):
    """Trích xuất dữ liệu CV từ form_data (phương thức cũ)"""
    form_data = content.get('form_data', {})
    
    cv_data = {
        'id': cv.id,
        'title': cv.title,
        'template_id': cv.template_id,
        'template_name': cv.get_template_name(),
        'updated_at': format_time_ago(cv.updated_at),
        'views': cv.views,
        'downloads': cv.downloads,
        
        # Thông tin cá nhân
        'full_name': form_data.get('full_name', ''),
        'position': form_data.get('position', ''),
        'email': form_data.get('email', ''),
        'phone': form_data.get('phone', ''),
        'address': form_data.get('address', ''),
        'website': form_data.get('website', ''),
        'summary': form_data.get('summary', ''),
        
        # Kinh nghiệm
        'experience': form_data.get('experience', []),
        
        # Học vấn
        'education': form_data.get('education', []),
        
        # Kỹ năng
        'technical_skills': format_skills_for_display(form_data.get('technical_skills', [])),
        'soft_skills': format_skills_for_display(form_data.get('soft_skills', [])),
        
        # Ngôn ngữ
        'languages': format_languages_for_display(form_data.get('languages', []))
    }
    
    return cv_data


def extract_cv_data_from_template_data(cv, content):
    """Trích xuất dữ liệu CV từ template_data"""
    template_data = content.get('template_data', {})
    form_data = content.get('form_data', {})
    
    # Khởi tạo cv_data với thông tin cơ bản
    cv_data = {
        'id': cv.id,
        'title': cv.title,
        'template_id': cv.template_id,
        'template_name': cv.get_template_name(),
        'updated_at': format_time_ago(cv.updated_at),
        'views': cv.views,
        'downloads': getattr(cv, 'downloads', 0),
        
        # Khởi tạo các trường dữ liệu
        'full_name': '',
        'position': '',
        'email': '',
        'phone': '',
        'address': '',
        'website': '',
        'summary': '',
        'experience': [],
        'education': [],
        'technical_skills': [],
        'soft_skills': [],
        'languages': []
    }
    
    # Ưu tiên sử dụng form_data nếu có
    if form_data:
        cv_data.update({
            'full_name': form_data.get('full_name', ''),
            'position': form_data.get('position', ''),
            'email': form_data.get('email', ''),
            'phone': form_data.get('phone', ''),
            'address': form_data.get('address', ''),
            'website': form_data.get('website', ''),
            'summary': form_data.get('summary', ''),
            'experience': form_data.get('experience', []),
            'education': form_data.get('education', []),
            'technical_skills': format_skills_for_display(form_data.get('technical_skills', [])),
            'soft_skills': format_skills_for_display(form_data.get('soft_skills', [])),
            'languages': format_languages_for_display(form_data.get('languages', []))
        })
        return cv_data
    
    # Nếu không có form_data, trích xuất từ template_data
    if 'children' in template_data:
        # Duyệt qua các layer
        for layer in template_data.get('children', []):
            # Duyệt qua các phần tử trong layer
            for element in layer.get('children', []):
                if element.get('className') == 'Text':
                    attrs = element.get('attrs', {})
                    element_id = attrs.get('id', '')
                    text = attrs.get('text', '')
                    
                    # Trích xuất thông tin cá nhân
                    if element_id == 'full_name':
                        cv_data['full_name'] = text
                    elif element_id == 'position':
                        cv_data['position'] = text
                    elif element_id == 'email':
                        # Loại bỏ icon email nếu có
                        cv_data['email'] = text.replace('✉ ', '').replace('✉', '').strip()
                    elif element_id == 'phone':
                        # Loại bỏ icon phone nếu có
                        cv_data['phone'] = text.replace('📞 ', '').replace('📞', '').strip()
                    elif element_id == 'address':
                        # Loại bỏ icon address nếu có
                        cv_data['address'] = text.replace('📍 ', '').replace('📍', '').strip()
                    elif element_id == 'website':
                        cv_data['website'] = text
                    elif element_id == 'summary':
                        cv_data['summary'] = text
                    
                    # Trích xuất kinh nghiệm làm việc
                    elif 'exp' in element_id:
                        extract_experience_from_template(cv_data, element_id, '', text)
                    
                    # Trích xuất học vấn
                    elif 'edu' in element_id:
                        extract_education_from_template(cv_data, element_id, '', text)
    
    return cv_data


def extract_experience_from_template(cv_data, element_id, field, text):
    """Trích xuất thông tin kinh nghiệm từ template elements"""
    # Xác định index của experience từ element_id (exp1 -> index 0, exp2 -> index 1)
    index_match = re.search(r'exp(\d+)', element_id)
    if not index_match:
        return
    
    index = int(index_match.group(1)) - 1  # Convert to 0-based index (exp1 -> 0, exp2 -> 1)
    
    # Đảm bảo experience list đủ lớn
    while len(cv_data['experience']) <= index:
        cv_data['experience'].append({
            'company': '',
            'position': '',
            'start_date': '',
            'end_date': '',
            'description': ''
        })
    
    # Xác định trường dữ liệu
    if 'position' in element_id or 'experience[' in field and '.position' in field:
        cv_data['experience'][index]['position'] = text
    elif 'company' in element_id or 'experience[' in field and '.company' in field:
        cv_data['experience'][index]['company'] = text
    elif 'date' in element_id or 'experience[' in field and '.dates' in field:
        # Tách start_date và end_date từ text như "2023-07 - "
        dates = text.split(' - ')
        cv_data['experience'][index]['start_date'] = dates[0].strip() if len(dates) > 0 else ''
        cv_data['experience'][index]['end_date'] = dates[1].strip() if len(dates) > 1 else ''
    elif 'description' in element_id or 'experience[' in field and '.description' in field:
        cv_data['experience'][index]['description'] = text


def extract_education_from_template(cv_data, element_id, field, text):
    """Trích xuất thông tin học vấn từ template elements"""
    # Xác định index của education từ element_id (edu1 -> index 0, edu2 -> index 1)
    index_match = re.search(r'edu(\d+)', element_id)
    if not index_match:
        return
    
    index = int(index_match.group(1)) - 1  # Convert to 0-based index (edu1 -> 0, edu2 -> 1)
    
    # Đảm bảo education list đủ lớn
    while len(cv_data['education']) <= index:
        cv_data['education'].append({
            'school': '',
            'degree': '',
            'start_date': '',
            'end_date': '',
            'description': ''
        })
    
    # Xác định trường dữ liệu
    if 'degree' in element_id or 'education[' in field and '.degree' in field:
        cv_data['education'][index]['degree'] = text
    elif 'school' in element_id or 'education[' in field and '.school' in field:
        cv_data['education'][index]['school'] = text
    elif 'date' in element_id or 'education[' in field and '.dates' in field:
        # Tách start_date và end_date từ text như "2019-09 - 2023-06"
        dates = text.split(' - ')
        cv_data['education'][index]['start_date'] = dates[0].strip() if len(dates) > 0 else ''
        cv_data['education'][index]['end_date'] = dates[1].strip() if len(dates) > 1 else ''
    elif 'description' in element_id or 'education[' in field and '.description' in field:
        cv_data['education'][index]['description'] = text


