import os
import json
import copy
from dotenv import load_dotenv
from google.genai import Client

class GeminiAI:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API key from environment variables
        self.api_key = os.getenv('API_KEY')
        
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
        
        # Initialize the client with API key
        self.client = Client(api_key=self.api_key)
    
    def extract_text_from_json(self, data):
        """
        Extract text attributes from elements with className 'Text'
        
        Args:
            data: JSON data structure containing template_data
            
        Returns:
            dict: Dictionary with element IDs as keys and text content as values
        """
        text_elements = {}
        
        def traverse_elements(element):
            """Recursively traverse the JSON structure to find Text elements"""
            if isinstance(element, dict):
                # Check if this is a Text element
                if element.get('className') == 'Text':
                    attrs = element.get('attrs', {})
                    element_id = attrs.get('id', 'unknown')
                    text_content = attrs.get('text', '')
                    text_elements[element_id] = text_content
                
                # Continue traversing children
                if 'children' in element:
                    for child in element['children']:
                        traverse_elements(child)
            
            elif isinstance(element, list):
                for item in element:
                    traverse_elements(item)
        
        # Start traversal from template_data
        if 'template_data' in data:
            traverse_elements(data['template_data'])
        
        return text_elements

    def extract_text_list_from_json(self, data):
        """
        Extract text attributes as a simple list
        
        Args:
            data: JSON data structure containing template_data
            
        Returns:
            list: List of text content from Text elements
        """
        text_list = []
        
        def traverse_elements(element):
            if isinstance(element, dict):
                if element.get('className') == 'Text':
                    attrs = element.get('attrs', {})
                    text_content = attrs.get('text', '')
                    if text_content:  # Only add non-empty text
                        text_list.append(text_content)
                
                if 'children' in element:
                    for child in element['children']:
                        traverse_elements(child)
            
            elif isinstance(element, list):
                for item in element:
                    traverse_elements(item)
        
        if 'template_data' in data:
            traverse_elements(data['template_data'])
        
        return text_list

    def extract_text_with_ids(self, data):
        """
        Extract text attributes with their IDs as list of tuples
        
        Args:
            data: JSON data structure containing template_data
            
        Returns:
            list: List of tuples (id, text) from Text elements
        """
        text_tuples = []
        
        def traverse_elements(element):
            if isinstance(element, dict):
                if element.get('className') == 'Text':
                    attrs = element.get('attrs', {})
                    element_id = attrs.get('id', 'unknown')
                    text_content = attrs.get('text', '')
                    text_tuples.append((element_id, text_content))
                
                if 'children' in element:
                    for child in element['children']:
                        traverse_elements(child)
            
            elif isinstance(element, list):
                for item in element:
                    traverse_elements(item)
        
        if 'template_data' in data:
            traverse_elements(data['template_data'])
        
        return text_tuples
    
    def evaluate_cv(self, cv_data):
        """
        Evaluate a CV using Gemini AI
        
        Args:
            cv_data: JSON data structure containing CV information
            
        Returns:
            dict: Evaluation result with scores and suggestions
        """
        try:
            # Extract text content from CV
            # text_elements = self.extract_text_from_json(cv_data)
            text_list = self.extract_text_list_from_json(cv_data)
            
            # Combine all text content
            cv_content = "\n".join(text_list)
            
            if not cv_content.strip():
                return {
                    "overall_score": 0,
                    "section_scores": {},
                    "suggestions": ["CV không có nội dung để đánh giá"]
                }
            
            # Create evaluation prompt
            prompt = f"""
    Hãy đánh giá CV sau đây và trả về kết quả dưới dạng JSON với cấu trúc như sau:
    {{
        "overall_score": <điểm tổng từ 0-100>,
        "section_scores": {{
            "personal_info": <điểm từ 0-100>,
            "work_experience": <điểm từ 0-100>,
            "education": <điểm từ 0-100>,
            "skills": <điểm từ 0-100>,
            "presentation": <điểm từ 0-100>
        }},
        "suggestions": [
            "<gợi ý cải thiện ngắn gọn 1>",
            "<gợi ý cải thiện ngắn gọn 2>",
            "<gợi ý cải thiện ngắn gọn 3>"
        ]
    }}

    Tiêu chí đánh giá:
    - Personal Info (20%): Thông tin cá nhân đầy đủ, chuyên nghiệp
    - Work Experience (30%): Kinh nghiệm làm việc chi tiết, có kết quả cụ thể
    - Education (20%): Học vấn phù hợp, có chứng chỉ
    - Skills (20%): Kỹ năng phù hợp với công việc
    - Presentation (10%): Trình bày rõ ràng, dễ đọc

    Nội dung CV:
    {cv_content}

    Chỉ trả về JSON, không giải thích thêm.
    """
            
            # Generate evaluation using Gemini AI
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            
            # Extract and parse the response
            result_text = response.text.strip()
            
            # Try to parse JSON from response
            try:
                # Remove any markdown formatting if present
                if result_text.startswith('```json'):
                    result_text = result_text.replace('```json', '').replace('```', '').strip()
                elif result_text.startswith('```'):
                    result_text = result_text.replace('```', '').strip()
                
                evaluation_result = json.loads(result_text)
                
                # Validate and ensure all required fields exist
                if not isinstance(evaluation_result, dict):
                    raise ValueError("Invalid response format")
                
                # Ensure overall_score exists and is valid
                if 'overall_score' not in evaluation_result:
                    evaluation_result['overall_score'] = 50
                
                # Ensure section_scores exists
                if 'section_scores' not in evaluation_result:
                    evaluation_result['section_scores'] = {
                        "personal_info": 50,
                        "work_experience": 50,
                        "education": 50,
                        "skills": 50,
                        "presentation": 50
                    }
                
                # Ensure suggestions exists
                if 'suggestions' not in evaluation_result:
                    evaluation_result['suggestions'] = ["Cần cải thiện thêm nội dung CV"]
                
                return evaluation_result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "overall_score": 50,
                    "section_scores": {
                        "personal_info": 50,
                        "work_experience": 50,
                        "education": 50,
                        "skills": 50,
                        "presentation": 50
                    },
                    "suggestions": [
                        "Bổ sung thêm thông tin cá nhân",
                        "Chi tiết hóa kinh nghiệm làm việc",
                        "Cải thiện cách trình bày"
                    ]
                }
        
        except Exception as e:
            print(f"Error evaluating CV: {str(e)}")
            return {
                "overall_score": 0,
                "section_scores": {
                    "personal_info": 0,
                    "work_experience": 0,
                    "education": 0,
                    "skills": 0,
                    "presentation": 0
                },
                "suggestions": [
                    "Có lỗi xảy ra khi đánh giá CV",
                    "Vui lòng kiểm tra lại nội dung CV",
                    "Thử lại sau"
                ]
            }
        
    def generate_text(self, prompt):
        """Generate text using Gemini API"""
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating text: {e}")
            return None
    
    def update_json_content_by_id(self, json_data, update_tuples):
        """
        Cập nhật nội dung các phần tử trong cấu trúc JSON dựa trên danh sách tuple (id, text).
        
        Args:
            json_data (dict): Dữ liệu JSON cần cập nhật
            update_tuples (list): Danh sách các tuple dạng (id, text)
        
        Returns:
            dict: Dữ liệu JSON đã được cập nhật
        """
        
        # Tạo bản sao sâu để không ảnh hưởng đến dữ liệu gốc
        updated_data = copy.deepcopy(json_data)
        
        # Tạo dictionary để tra cứu nhanh
        update_dict = dict(update_tuples)
        
        def update_recursive(obj):
            """
            Hàm đệ quy để duyệt qua tất cả các phần tử trong cấu trúc JSON
            """
            if isinstance(obj, dict):
                # Kiểm tra nếu object có thuộc tính 'id' và 'text'
                if 'id' in obj and obj['id'] in update_dict:
                    # Cập nhật nội dung text
                    if 'text' in obj:
                        obj['text'] = update_dict[obj['id']]
                        print(f"Đã cập nhật ID '{obj['id']}': {update_dict[obj['id']]}")
                
                # Đệ quy cho tất cả các giá trị trong dictionary
                for key, value in obj.items():
                    update_recursive(value)
                    
            elif isinstance(obj, list):
                # Đệ quy cho tất cả các phần tử trong list
                for item in obj:
                    update_recursive(item)
        
        # Bắt đầu quá trình cập nhật
        update_recursive(updated_data)
        
        return updated_data

    def print_updated_elements(self, json_data, update_tuples):
        """
        In ra các phần tử đã được cập nhật để kiểm tra
        """
        update_dict = dict(update_tuples)
        
        def find_elements_recursive(obj, path=""):
            found_elements = []
            
            if isinstance(obj, dict):
                if 'id' in obj and obj['id'] in update_dict:
                    found_elements.append({
                        'path': path,
                        'id': obj['id'],
                        'old_text': obj.get('text', 'N/A'),
                        'new_text': update_dict[obj['id']]
                    })
                
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    found_elements.extend(find_elements_recursive(value, new_path))
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    found_elements.extend(find_elements_recursive(item, new_path))
            
            return found_elements
        
        elements = find_elements_recursive(json_data)
        
        print("Các phần tử sẽ được cập nhật:")
        print("-" * 80)
        for element in elements:
            print(f"ID: {element['id']}")
            print(f"Path: {element['path']}")
            print(f"Nội dung cũ: {element['old_text']}")
            print(f"Nội dung mới: {element['new_text']}")
            print("-" * 40)
    
    def translate_text(self, cv_data, target_language='vi'):
        """
        Dịch văn bản sang ngôn ngữ đích sử dụng Gemini AI
        
        Args:
            cv_data: JSON data structure containing CV information
            target_language (str): Mã ngôn ngữ đích (mặc định là 'vi' cho tiếng Việt)
        
        Returns:
            dict: Dữ liệu JSON đã được cập nhật với nội dung đã dịch
        """
        try:
            # Trích xuất text elements với IDs
            text_tuples = self.extract_text_with_ids(cv_data)
            
            if not text_tuples:
                return cv_data  # Trả về dữ liệu gốc nếu không có text để dịch
            
            # Tạo mapping ngôn ngữ
            language_map = {
                'vi': 'Vietnamese',
                'en': 'English',
                'fr': 'French',
                'de': 'German',
                'es': 'Spanish',
                'ja': 'Japanese',
                'ko': 'Korean',
                'zh': 'Chinese'
            }
            
            target_lang_name = language_map.get(target_language, 'Vietnamese')
            
            # Tạo danh sách text cần dịch
            texts_to_translate = [text for _, text in text_tuples if text.strip()]
            
            if not texts_to_translate:
                return cv_data
            
            # Tạo prompt dịch
            texts_json = json.dumps(texts_to_translate, ensure_ascii=False)
            prompt = f"""
Dịch danh sách văn bản sau sang {target_lang_name}. Trả về kết quả dưới dạng JSON array với cùng thứ tự:

Văn bản cần dịch:
{texts_json}

Yêu cầu:
- Giữ nguyên định dạng và cấu trúc
- Dịch chính xác và tự nhiên
- Chỉ trả về JSON array, không giải thích thêm
- Giữ nguyên các ký tự đặc biệt như dấu gạch đầu dòng, số, v.v.
"""
            
            # Gọi Gemini AI để dịch
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            
            # Parse response
            result_text = response.text.strip()
            
            # Xử lý markdown formatting nếu có
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            translated_texts = json.loads(result_text)
            
            # Tạo danh sách tuple cập nhật
            update_tuples = []
            translated_index = 0
            
            for element_id, original_text in text_tuples:
                if original_text.strip():
                    if translated_index < len(translated_texts):
                        update_tuples.append((element_id, translated_texts[translated_index]))
                        translated_index += 1
                    else:
                        update_tuples.append((element_id, original_text))  # Giữ nguyên nếu không có bản dịch
                else:
                    update_tuples.append((element_id, original_text))  # Giữ nguyên text rỗng
            
            # Cập nhật JSON với nội dung đã dịch
            updated_cv_data = self.update_json_content_by_id(cv_data, update_tuples)
            
            return updated_cv_data
            
        except Exception as e:
            print(f"Error translating CV: {str(e)}")
            return cv_data  # Trả về dữ liệu gốc nếu có lỗi