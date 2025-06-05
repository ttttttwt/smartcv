import os
import platform
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

def get_system_font_path(font_name):
    """Try to find a system font file based on OS."""
    # Common font filenames
    font_variants = {
        'Arial': ['arial.ttf', 'Arial.ttf', 'ARIAL.TTF'],
        'Arial-Bold': ['arialbd.ttf', 'Arial Bold.ttf', 'Arial_Bold.ttf', 'ARIALBD.TTF'],
        'Times New Roman': ['times.ttf', 'Times New Roman.ttf', 'TimesNewRoman.ttf'],
        'Times New Roman-Bold': ['timesbd.ttf', 'Times New Roman Bold.ttf'],
        'Roboto': ['Roboto-Regular.ttf'],
        'Roboto-Bold': ['Roboto-Bold.ttf'],
        'DejaVuSans': ['DejaVuSans.ttf'],
        'DejaVuSans-Bold': ['DejaVuSans-Bold.ttf'],
    }
    
    # Add Vietnamese font support
    if platform.system() == 'Windows':
        font_variants.update({
            'Arial Unicode MS': ['ARIALUNI.TTF', 'arialuni.ttf'],
            'Times New Roman Unicode': ['TIMESUNI.TTF', 'timesuni.ttf'],
        })
    
    # Different font directories by OS
    if platform.system() == 'Windows':
        font_dirs = [
            'C:\\Windows\\Fonts',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Windows\\Fonts')
        ]
    elif platform.system() == 'Darwin':  # macOS
        font_dirs = [
            '/Library/Fonts',
            '/System/Library/Fonts',
            os.path.expanduser('~/Library/Fonts')
        ]
    else:  # Linux
        font_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts')
        ]
    
    # Check each possible location
    for font_dir in font_dirs:
        if not os.path.exists(font_dir):
            continue
            
        variants = font_variants.get(font_name, [])
        if not variants:
            # If no variants defined, try the font name directly
            variants = [f"{font_name}.ttf", f"{font_name.lower()}.ttf"]
        
        for variant in variants:
            font_path = os.path.join(font_dir, variant)
            if os.path.exists(font_path):
                return font_path
    
    return None

def setup_fonts_for_unicode():
    """Register fonts with good Unicode support for Vietnamese."""
    fonts_registered = False
    
    # Try to register Arial and Arial Bold (good Unicode support)
    arial_path = get_system_font_path('Arial')
    arial_bold_path = get_system_font_path('Arial-Bold')
    
    if arial_path and arial_bold_path:
        try:
            pdfmetrics.registerFont(TTFont('Arial', arial_path))
            pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
            addMapping('Arial', 0, 0, 'Arial')
            addMapping('Arial', 1, 0, 'Arial-Bold')
            fonts_registered = True
        except Exception as e:
            print(f"Error registering Arial fonts: {e}")
    
    # If Arial failed, try Times New Roman (good for Vietnamese)
    if not fonts_registered:
        times_path = get_system_font_path('Times New Roman')
        times_bold_path = get_system_font_path('Times New Roman-Bold')
        
        if times_path and times_bold_path:
            try:
                pdfmetrics.registerFont(TTFont('Times New Roman', times_path))
                pdfmetrics.registerFont(TTFont('Times New Roman-Bold', times_bold_path))
                addMapping('Times New Roman', 0, 0, 'Times New Roman')
                addMapping('Times New Roman', 1, 0, 'Times New Roman-Bold')
                fonts_registered = True
            except Exception as e:
                print(f"Error registering Times New Roman fonts: {e}")
    
    # Try specialized Unicode fonts
    if not fonts_registered:
        arial_unicode_path = get_system_font_path('Arial Unicode MS')
        if arial_unicode_path:
            try:
                pdfmetrics.registerFont(TTFont('Arial Unicode MS', arial_unicode_path))
                fonts_registered = True
            except Exception as e:
                print(f"Error registering Arial Unicode MS: {e}")
    
    # Last resort - DejaVu Sans (good Unicode support)
    if not fonts_registered:
        dejavu_path = get_system_font_path('DejaVuSans')
        dejavu_bold_path = get_system_font_path('DejaVuSans-Bold')
        
        if dejavu_path:
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))
                if dejavu_bold_path:
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold_path))
                    addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')
                fonts_registered = True
            except Exception as e:
                print(f"Error registering DejaVu fonts: {e}")
    
    # Return the best font family to use as default
    if 'Arial' in pdfmetrics._fonts:
        return 'Arial'
    elif 'Times New Roman' in pdfmetrics._fonts:
        return 'Times New Roman'
    elif 'Arial Unicode MS' in pdfmetrics._fonts:
        return 'Arial Unicode MS'
    elif 'DejaVuSans' in pdfmetrics._fonts:
        return 'DejaVuSans'
    else:
        # If nothing worked, return Helvetica (built-in)
        return 'Helvetica'
