import json
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz  # PyMuPDF

class KonvaJSONToPDF:
    def __init__(self, dpi=72):
        """
        Initialize converter with DPI setting
        Args:
            dpi: Dots per inch, default 96 for web standard
        """
        self.dpi = dpi
        self.px_to_point = 72 / dpi  # Convert pixel to point
        self.canvas = None
        self.unicode_font = None
        self.regular_font = None
        self.bold_font = None
        
    def px_to_pt(self, px_value):
        """Convert pixel to point"""
        return px_value * self.px_to_point
    
    def hex_to_color(self, hex_string):
        """Convert hex color to ReportLab color"""
        if hex_string and hex_string.startswith('#'):
            return HexColor(hex_string)
        return HexColor('#000000')  # Default black
    
    def is_unicode_character(self, char):
        """Check if character needs Unicode font support"""
        if not char:
            return False
        
        char_code = ord(char)
        
        # Common icon/emoji ranges
        unicode_ranges = [
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F680, 0x1F6FF),  # Transport and Map
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0xE000, 0xF8FF),    # Private Use Area (custom icons)
            (0xF000, 0xF8FF),    # Private Use Area extended
        ]
        
        return any(start <= char_code <= end for start, end in unicode_ranges)
    
    def setup_fonts(self):
        """Setup fonts for PDF with Unicode support"""
        # Default fonts
        self.regular_font = 'Helvetica'
        self.bold_font = 'Helvetica-Bold'
        self.unicode_font = 'Helvetica'  # Fallback
        
        try:
            windir = os.environ.get('WINDIR', '')
            if windir:
                # Try to register Arial with better Unicode support
                arial_path = os.path.join(windir, 'Fonts', 'arial.ttf')
                arial_bold_path = os.path.join(windir, 'Fonts', 'arialbd.ttf')
                
                if os.path.exists(arial_path):
                    pdfmetrics.registerFont(TTFont('Arial', arial_path))
                    self.regular_font = 'Arial'
                    
                if os.path.exists(arial_bold_path):
                    pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
                    self.bold_font = 'Arial-Bold'
                
                # Try to register fonts with better Unicode/icon support
                unicode_fonts = [
                    ('Segoe UI Symbol', os.path.join(windir, 'Fonts', 'seguisym.ttf')),
                    ('Segoe UI Emoji', os.path.join(windir, 'Fonts', 'seguiemj.ttf')),
                    ('Arial Unicode MS', os.path.join(windir, 'Fonts', 'ARIALUNI.TTF')),
                ]
                
                for font_name, font_path in unicode_fonts:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            self.unicode_font = font_name
                            print(f"Registered Unicode font: {font_name}")
                            break
                        except Exception as e:
                            print(f"Failed to register {font_name}: {e}")
                            continue
                            
        except Exception as e:
            print(f"Font registration failed: {e}")
    
    def draw_rect(self, attrs):
        """Draw rectangle"""
        if not self.canvas:
            return
            
        x = self.px_to_pt(attrs.get('x', 0))
        y = self.px_to_pt(attrs.get('y', 0))
        width = self.px_to_pt(attrs.get('width', 0))
        height = self.px_to_pt(attrs.get('height', 0))
        
        # ReportLab has inverted coordinate system (y increases from bottom)
        # Need to flip y coordinate
        page_height = self.canvas._pagesize[1]  # Get actual page height
        y = page_height - y - height
        
        # Set fill color
        fill_color = attrs.get('fill')
        if fill_color:
            self.canvas.setFillColor(self.hex_to_color(fill_color))
        
        # Set stroke
        stroke_width = attrs.get('strokeWidth', 0)
        if stroke_width > 0:
            self.canvas.setLineWidth(self.px_to_pt(stroke_width))
            stroke_color = attrs.get('stroke', '#000000')
            self.canvas.setStrokeColor(self.hex_to_color(stroke_color))
            self.canvas.rect(x, y, width, height, fill=1, stroke=1)
        else:
            self.canvas.rect(x, y, width, height, fill=1, stroke=0)
    
    def draw_text_with_icons(self, text, x, y, font_name, font_size, color):
        """Draw text that may contain icons/Unicode characters"""
        self.canvas.setFillColor(color)
        
        current_x = x
        text_buffer = ""
        current_font = font_name
        
        for char in text:
            if self.is_unicode_character(char):
                # Draw accumulated regular text first
                if text_buffer:
                    self.canvas.setFont(current_font, font_size)
                    self.canvas.drawString(current_x, y, text_buffer)
                    current_x += self.canvas.stringWidth(text_buffer, current_font, font_size)
                    text_buffer = ""
                
                # Try to draw Unicode character with Unicode font
                try:
                    self.canvas.setFont(self.unicode_font, font_size)
                    self.canvas.drawString(current_x, y, char)
                    current_x += self.canvas.stringWidth(char, self.unicode_font, font_size)
                except:
                    # Fallback: draw placeholder or skip
                    self.canvas.setFont(current_font, font_size)
                    placeholder = "?"  # or could be empty string ""
                    self.canvas.drawString(current_x, y, placeholder)
                    current_x += self.canvas.stringWidth(placeholder, current_font, font_size)
            else:
                # Add to regular text buffer
                text_buffer += char
        
        # Draw any remaining regular text
        if text_buffer:
            self.canvas.setFont(current_font, font_size)
            self.canvas.drawString(current_x, y, text_buffer)
    
    def draw_text(self, attrs):
        """Draw text with improved Unicode support"""
        if not self.canvas:
            return
            
        x = self.px_to_pt(attrs.get('x', 0))
        y = self.px_to_pt(attrs.get('y', 0))
        text = attrs.get('text', '')
        font_size = attrs.get('fontSize', 12)
        
        # Flip y coordinate
        page_height = self.canvas._pagesize[1]
        y = page_height - y - self.px_to_pt(font_size)
        
        # Set font
        font_style = attrs.get('fontStyle', 'normal')
        if font_style == 'bold':
            font_name = self.bold_font
        else:
            font_name = self.regular_font
        
        # Set color
        fill_color = attrs.get('fill', '#000000')
        color = self.hex_to_color(fill_color)
        
        # Handle text wrapping
        width = self.px_to_pt(attrs.get('width', 500))
        line_height = attrs.get('lineHeight', 1.2)
        
        # Split text by lines if contains \r\n or \n
        lines = text.split('\r\n') if '\r\n' in text else text.split('\n')
        
        current_y = y
        for line in lines:
            if line.strip():  # Skip empty lines
                # Simple text wrapping with icon support
                words = line.split(' ')
                current_line = ''
                
                for word in words:
                    test_line = current_line + (' ' if current_line else '') + word
                    
                    # Estimate width (approximate for mixed content)
                    try:
                        text_width = self.canvas.stringWidth(test_line, font_name, font_size)
                    except:
                        text_width = len(test_line) * font_size * 0.6  # Rough estimate
                    
                    if text_width <= width:
                        current_line = test_line
                    else:
                        if current_line:
                            self.draw_text_with_icons(current_line, x, current_y, font_name, font_size, color)
                            current_y -= font_size * line_height
                        current_line = word
                
                if current_line:
                    self.draw_text_with_icons(current_line, x, current_y, font_name, font_size, color)
                    current_y -= font_size * line_height
            else:
                current_y -= font_size * line_height
    
    def process_children(self, children):
        """Process children elements"""
        for child in children:
            class_name = child.get('className', '')
            attrs = child.get('attrs', {})
            
            if class_name == 'Rect':
                self.draw_rect(attrs)
            elif class_name == 'Text':
                self.draw_text(attrs)
            elif class_name == 'Layer':
                # Recursively process layer children
                layer_children = child.get('children', [])
                self.process_children(layer_children)
    
    def convert_json_to_pdf(self, json_data, output_filename):
        """
        Convert Konva JSON to PDF
        Args:
            json_data: Dict or JSON string of Konva stage
            output_filename: PDF output filename
        """
        # Parse JSON if string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Get stage dimensions
        stage_attrs = data.get('attrs', {})
        stage_width = self.px_to_pt(stage_attrs.get('width', 595))
        stage_height = self.px_to_pt(stage_attrs.get('height', 842))
        
        # Create canvas
        self.canvas = canvas.Canvas(output_filename, pagesize=A4)
        print(f"Creating PDF with size: {stage_width}x{stage_height} points")
        # Setup fonts
        self.setup_fonts()
        
        # Process all children
        children = data.get('children', [])
        self.process_children(children)
        
        # Save PDF
        self.canvas.save()
        print(f"PDF created: {output_filename}")
    
    def convert_from_file(self, json_file_path, output_filename):
        """
        Convert from JSON file
        Args:
            json_file_path: Path to JSON file
            output_filename: PDF output filename
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        self.convert_json_to_pdf(json_data, output_filename)
    
    def convert_pdf_to_png(self, pdf_path, output_png_path=None, png_dpi=300, page_num=0):
        """
        Convert PDF to PNG image
        
        Args:
            pdf_path: Path to the PDF file
            output_png_path: Path where PNG should be saved (if None, uses PDF name with .png extension)
            png_dpi: Resolution for the PNG image (default 300)
            page_num: Page number to convert (default 0 - first page)
            
        Returns:
            Path to the created PNG file
        """
        if output_png_path is None:
            # If no output path specified, create one based on the PDF filename
            base_name = os.path.splitext(pdf_path)[0]
            output_png_path = f"{base_name}.png"
        
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Check if page exists
        if page_num < len(doc):
            # Get the page
            page = doc[page_num]
            
            # Set the resolution - create a transformation matrix
            zoom_factor = png_dpi / 72  # 72 is the default PDF dpi
            matrix = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Get the pixmap (image)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Save the image
            pix.save(output_png_path)
            print(f"PNG created: {output_png_path}")
            
            # Close the document
            doc.close()
            
            return output_png_path
        else:
            doc.close()
            raise IndexError(f"Page {page_num} does not exist in the PDF document")
    
    def convert_json_to_png(self, json_data, output_png_path, pdf_path=None, delete_pdf=False, png_dpi=300):
        """
        Convert Konva JSON directly to PNG (through PDF)
        
        Args:
            json_data: Dict or JSON string of Konva stage
            output_png_path: PNG output filename
            pdf_path: Optional path for intermediate PDF (if None, temporary path will be used)
            delete_pdf: Whether to delete the intermediate PDF file
            png_dpi: Resolution for the PNG image
            
        Returns:
            Path to the created PNG file
        """
        # Create temporary PDF file if needed
        temp_pdf_file = None
        if pdf_path is None:
            # Use tempfile to create a temporary file that will be automatically cleaned up
            temp_pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_pdf_file.name
            temp_pdf_file.close()  # Close the file but keep it on disk
        
        try:
            # Convert JSON to PDF first
            self.convert_json_to_pdf(json_data, pdf_path)
            
            # Convert PDF to PNG
            png_path = self.convert_pdf_to_png(pdf_path, output_png_path, png_dpi)
            
            return png_path
        finally:
            # Delete intermediate PDF if it was a temporary file or if delete_pdf is True
            if (temp_pdf_file is not None or delete_pdf) and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    print(f"Removed intermediate PDF: {pdf_path}")
                except Exception as e:
                    print(f"Warning: Could not delete intermediate PDF {pdf_path}: {e}")

    def convert_file_to_png(self, json_file_path, output_png_path, pdf_path=None, delete_pdf=False, png_dpi=300):
        """
        Convert JSON file directly to PNG (through PDF)
        
        Args:
            json_file_path: Path to JSON file
            output_png_path: PNG output filename
            pdf_path: Optional path for intermediate PDF (if None, temporary path will be used)
            delete_pdf: Whether to delete the intermediate PDF file
            png_dpi: Resolution for the PNG image
            
        Returns:
            Path to the created PNG file
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        return self.convert_json_to_png(json_data, output_png_path, pdf_path, delete_pdf, png_dpi)

def generate_pdf_from_json(json_path, output_path=None):
    """Generate PDF from JSON file"""
    if output_path is None:
        # If no output path specified, create one based on the JSON filename
        base_name = os.path.splitext(json_path)[0]
        output_path = f"{base_name}.pdf"
    
    # Create converter
    converter = KonvaJSONToPDF(dpi=72)
    
    # Convert to PDF
    converter.convert_from_file(json_path, output_path)
    return output_path

def convert_pdf_to_png(pdf_path, output_path=None, dpi=300, page_num=0):
    """
    Convert PDF to PNG image
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path where PNG should be saved (if None, uses PDF name with .png extension)
        dpi: Resolution for the PNG image (default 300)
        page_num: Page number to convert (default 0 - first page)
        
    Returns:
        Path to the created PNG file
    """
    # Create converter instance
    converter = KonvaJSONToPDF()
    return converter.convert_pdf_to_png(pdf_path, output_path, dpi, page_num)

def generate_png_from_json(json_path, output_pdf_path=None, output_png_path=None, dpi=300, keep_pdf=True):
    """
    Complete workflow to convert JSON to PNG through PDF
    
    Args:
        json_path: Path to the JSON file
        output_pdf_path: Path for the intermediate PDF file (if None, will be generated)
        output_png_path: Path for the final PNG file (if None, will be generated)
        dpi: Resolution for the PNG image
        keep_pdf: Whether to keep the PDF file (and include in result)
        
    Returns:
        Dictionary with paths to both PDF and PNG files, or just PNG path if keep_pdf=False
    """
    if output_png_path is None:
        # If no output path specified, create one based on the JSON filename
        base_name = os.path.splitext(json_path)[0]
        output_png_path = f"{base_name}.png"
    
    converter = KonvaJSONToPDF(dpi=72)
    
    if keep_pdf:
        # Generate PDF first
        pdf_path = generate_pdf_from_json(json_path, output_pdf_path)
        
        # Then convert to PNG
        png_path = converter.convert_pdf_to_png(pdf_path, output_png_path, dpi)
        
        return {
            "pdf_path": pdf_path,
            "png_path": png_path
        }
    else:
        # Generate PNG directly (PDF will be temporary)
        png_path = converter.convert_file_to_png(
            json_path, 
            output_png_path, 
            pdf_path=output_pdf_path, 
            delete_pdf=True, 
            png_dpi=dpi
        )
        
        return {
            "png_path": png_path
        }

# Legacy function aliases for backward compatibility
def create_cv_pdf(json_path, output_path):
    """Legacy function - use generate_pdf_from_json instead"""
    return generate_pdf_from_json(json_path, output_path)

if __name__ == "__main__":
    # Example usage
    # 1. Just generate PDF
    # pdf_path = generate_pdf_from_json(json_path=r"test\test2.json", output_path=r"test\output.pdf")
    
    # 2. Convert existing PDF to PNG
    # convert_pdf_to_png(pdf_path=r"test\output.pdf", output_path=r"test\output.png", dpi=300)
    
    # 3. Complete workflow JSON -> PDF -> PNG (keeping PDF)
    # result = generate_png_from_json(json_path=r"test\test2.json", dpi=300, keep_pdf=True)
    # print(f"Generated files: PDF at {result['pdf_path']}, PNG at {result['png_path']}")
    
    # 4. Complete workflow JSON -> PNG (without keeping PDF)
    result = generate_png_from_json(json_path=r"test\test2.json", dpi=300, keep_pdf=False)
    print(f"Generated PNG file: {result['png_path']}")
