import json

def extract_text_from_json(data):
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

def extract_text_list_from_json(data):
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

def extract_text_with_ids(data):
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

# Example usage:
if __name__ == "__main__":
    # Load your JSON data
    with open('test/test.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Extract text as dictionary (ID -> text)
    text_dict = extract_text_from_json(json_data)
    print("Text elements with IDs:")
    for element_id, text in text_dict.items():
        print(f"{element_id}: {text}")
    
    print("\n" + "="*50 + "\n")
    
    # Extract text as simple list
    text_list = extract_text_list_from_json(json_data)
    print("All text content:")
    for i, text in enumerate(text_list, 1):
        print(f"{i}. {text}")
    
    print("\n" + "="*50 + "\n")
    
    # Extract text with IDs as tuples
    text_tuples = extract_text_with_ids(json_data)
    print("Text elements as (ID, text) tuples:")
    for element_id, text in text_tuples:
        print(f"({element_id}, '{text}')")
