"""Core QR code generation functionality"""

import qrcode
from PIL import Image, ImageDraw

class BusinessCardQRGenerator:
    """Custom QR Code Generator with design control for business cards."""
    
    def __init__(self, data, box_size=10, border=2):
        self.data = data
        self.box_size = box_size
        self.border = border
        
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        self.qr.add_data(data)
        self.qr.make(fit=True)
    
    def generate_basic(self, fill_color="black", back_color="white"):
        """Generate basic QR code with custom colors"""
        img = self.qr.make_image(fill_color=fill_color, back_color=back_color)
        return img.convert('RGB')
    
    def add_rounded_corners(self, img, radius=None, antialias_scale=4):
        """Add rounded corners to QR code pixels with anti-aliasing"""
        if radius is None:
            radius = self.box_size // 3
        
        matrix = self.qr.get_matrix()
        matrix_size = len(matrix)
        total_size = (matrix_size + 2 * self.border) * self.box_size
        
        scaled_size = total_size * antialias_scale
        scaled_box = self.box_size * antialias_scale
        scaled_radius = radius * antialias_scale
        
        rounded_img = Image.new('RGB', (scaled_size, scaled_size), 'white')
        draw = ImageDraw.Draw(rounded_img)
        
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value:
                    left = (self.border + x) * scaled_box
                    top = (self.border + y) * scaled_box
                    right = left + scaled_box
                    bottom = top + scaled_box
                    
                    draw.rounded_rectangle(
                        [(left, top), (right, bottom)],
                        radius=scaled_radius,
                        fill='black'
                    )
        
        rounded_img = rounded_img.resize(
            (total_size, total_size), 
            Image.Resampling.LANCZOS
        )
        
        return rounded_img
    
    def add_logo(self, img, logo_image, logo_size_ratio=0.2):
        """Add logo to center of QR code"""
        logo = logo_image.copy()
        
        qr_width, qr_height = img.size
        logo_size = int(min(qr_width, qr_height) * logo_size_ratio)
        
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        logo_bg_size = int(logo_size * 1.15)
        logo_bg = Image.new('RGB', (logo_bg_size, logo_bg_size), 'white')
        
        logo_pos = ((logo_bg_size - logo.width) // 2, (logo_bg_size - logo.height) // 2)
        logo_bg.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
        
        qr_center = ((qr_width - logo_bg_size) // 2, (qr_height - logo_bg_size) // 2)
        img.paste(logo_bg, qr_center)
        
        return img
    
    def add_gradient(self, img, color1=(0, 0, 0), color2=(100, 50, 200)):
        """Apply gradient color to QR code"""
        width, height = img.size
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        pixels = img.load()
        gradient_pixels = gradient.load()
        
        for y in range(height):
            for x in range(width):
                if pixels[x, y] == (0, 0, 0):
                    pixels[x, y] = gradient_pixels[x, y]
        
        return img
    
    def generate_custom(self, rounded=True, radius=None, logo_image=None,
                       gradient=False, color1=(0, 0, 0), color2=(100, 50, 200),
                       fill_color="black", back_color="white"):
        """Generate fully customized QR code"""
        if rounded:
            img = self.generate_basic(back_color=back_color)
            img = self.add_rounded_corners(img, radius)
        else:
            img = self.generate_basic(fill_color=fill_color, back_color=back_color)
        
        if gradient:
            img = self.add_gradient(img, color1, color2)
        
        if logo_image:
            img = self.add_logo(img, logo_image)
        
        return img