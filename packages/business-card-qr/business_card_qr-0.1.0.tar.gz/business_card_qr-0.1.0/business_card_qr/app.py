"""
Business Card QR Code Generator - Streamlit App
Run with: streamlit run app.py
"""

import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io

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


def generate_vcard(full_name, company, title, phone, email, website, address):
    """Generate vCard string"""
    vcard = 'BEGIN:VCARD\n'
    vcard += 'VERSION:3.0\n'
    vcard += f'FN:{full_name}\n'
    
    if company:
        vcard += f'ORG:{company}\n'
    if title:
        vcard += f'TITLE:{title}\n'
    if phone:
        vcard += f'TEL:{phone}\n'
    if email:
        vcard += f'EMAIL:{email}\n'
    if website:
        vcard += f'URL:{website}\n'
    if address:
        vcard += f'ADR:;;{address}\n'
    
    vcard += 'END:VCARD'
    return vcard


def run_app():
    """Main Streamlit app function"""
    st.set_page_config(
        page_title="Business Card QR Generator",
        page_icon="🎴",
        layout="wide"
    )
    
    st.title("🎴 Business Card QR Code Generator")
    st.markdown("Create professional vCard QR codes with custom styling")
    
    # Two column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Contact Information")
        
        full_name = st.text_input("Full Name *", placeholder="John Doe")
        company = st.text_input("Company / Organization", placeholder="Example Company")
        title = st.text_input("Job Title", placeholder="Software Engineer")
        phone = st.text_input("Phone Number", placeholder="+1-234-567-8900")
        email = st.text_input("Email Address", placeholder="john.doe@example.com")
        website = st.text_input("Website", placeholder="https://www.example.com")
        address = st.text_area("Address", placeholder="123 Main Street, City, State, ZIP")
        
        st.header("🎨 Styling Options")
        
        rounded = st.checkbox("Rounded corners", value=True)
        
        use_gradient = st.checkbox("Use gradient colors")
        
        if use_gradient:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                color1 = st.color_picker("Gradient Start", "#1a1a1a")
            with col_g2:
                color2 = st.color_picker("Gradient End", "#764ba2")
        else:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                fg_color = st.color_picker("QR Color", "#000000")
            with col_c2:
                bg_color = st.color_picker("Background", "#ffffff")
        
        st.header("🖼️ Logo (Optional)")
        logo_file = st.file_uploader(
            "Upload Logo (PNG/JPG)",
            type=['png', 'jpg', 'jpeg'],
            help="Logo should be under 25% of QR code size for best scannability"
        )
        
        logo_size_ratio = 0.20  # Default
        if logo_file:
            logo_size_ratio = st.slider(
                "Logo Size (%)",
                min_value=10,
                max_value=25,
                value=20,
                help="Larger logos may affect scannability"
            ) / 100
        
        generate_btn = st.button("🚀 Generate QR Code", type="primary", use_container_width=True)
    
    with col2:
        st.header("👁️ Preview")
        
        if generate_btn:
            if not full_name:
                st.error("Please enter at least a full name")
            else:
                with st.spinner("Generating QR code..."):
                    # Generate vCard
                    vcard_data = generate_vcard(
                        full_name, company, title, phone, email, website, address
                    )
                    
                    # Create QR generator
                    qr_gen = BusinessCardQRGenerator(vcard_data, box_size=10, border=2)
                    
                    # Load logo if provided
                    logo_image = None
                    if logo_file:
                        logo_image = Image.open(logo_file)
                    
                    # Generate QR code with proper logo size
                    if use_gradient:
                        # Convert hex to RGB
                        c1 = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                        c2 = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                        
                        # Generate base QR first
                        qr_img = qr_gen.generate_custom(
                            rounded=rounded,
                            gradient=True,
                            color1=c1,
                            color2=c2,
                            logo_image=None
                        )
                        
                        # Add logo with custom size if provided
                        if logo_image:
                            qr_img = qr_gen.add_logo(qr_img, logo_image, logo_size_ratio)
                    else:
                        # Generate base QR first
                        qr_img = qr_gen.generate_custom(
                            rounded=rounded,
                            fill_color=fg_color,
                            back_color=bg_color,
                            logo_image=None
                        )
                        
                        # Add logo with custom size if provided
                        if logo_image:
                            qr_img = qr_gen.add_logo(qr_img, logo_image, logo_size_ratio)
                    
                    # Display QR code
                    st.image(qr_img, use_container_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    qr_img.save(buf, format='PNG')
                    byte_im = buf.getvalue()
                    
                    filename = f"{full_name.replace(' ', '_')}_business_card_qr.png"
                    st.download_button(
                        label="📥 Download QR Code",
                        data=byte_im,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    st.success("✅ QR Code generated successfully!")
                    st.info("📱 Test by scanning with your phone camera")
        else:
            st.info("Fill in the contact information and click 'Generate QR Code'")

def main():
    """Entry point for console script"""
    run_app()


if __name__ == "__main__":
    run_app()