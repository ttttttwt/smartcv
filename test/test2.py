import json
import copy

def update_json_content_by_id(json_data, update_tuples):
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

def print_updated_elements(json_data, update_tuples):
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

# Ví dụ sử dụng
if __name__ == "__main__":
    # Dữ liệu JSON mẫu (sử dụng dữ liệu từ file bạn cung cấp)
    sample_json = {
        "template_data": {
            "attrs": {"width": 595, "height": 842},
            "className": "Stage",
            "children": [
                {
                    "attrs": {},
                    "className": "Layer",
                    "children": [
                        {
                            "attrs": {
                                "x": 40,
                                "y": 25,
                                "text": "Nguyễn Văn A",
                                "fontSize": 28,
                                "fontStyle": "bold",
                                "fill": "#FFFFFF",
                                "width": 350,
                                "wrap": "none",
                                "lineHeight": 1.2,
                                "id": "full_name"
                            },
                            "className": "Text"
                        },
                        {
                            "attrs": {
                                "x": 40,
                                "y": 65,
                                "text": "Frontend Developer",
                                "fontSize": 16,
                                "fill": "#E5E7EB",
                                "width": 350,
                                "wrap": "none",
                                "lineHeight": 1.2,
                                "id": "position"
                            },
                            "className": "Text"
                        }
                    ]
                }
            ]
        }
    }
    
    # Danh sách tuple cập nhật
    update_list = [
        ('full_name', 'Nguyễn Văn B'),
        ('position', 'Senior Frontend Developer'),
        ('email', '✉ nguyenvanb@email.com'),
        ('phone', '📞 0123456789'),
        ('address', '📍 Quận 2, TP.HCM')
    ]
    
    # In ra các phần tử sẽ được cập nhật
    print_updated_elements(sample_json, update_list)
    
    # Thực hiện cập nhật
    updated_json = update_json_content_by_id(sample_json, update_list)
    
    # In kết quả
    print("\nDữ liệu JSON sau khi cập nhật:")
    print(json.dumps(updated_json, indent=2, ensure_ascii=False))