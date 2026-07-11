import os
from PIL import Image, ImageDraw, ImageFont

def draw_gradient_and_shapes(width, height, color1, color2, course_name):
    # Create background image
    base = Image.new("RGBA", (width, height), color=0)
    draw = ImageDraw.Draw(base)
    
    # Draw linear gradient (top-left to bottom-right)
    for y in range(height):
        # Interpolate colors
        r = int(color1[0] + (color2[0] - color1[0]) * (y / height))
        g = int(color1[1] + (color2[1] - color1[1]) * (y / height))
        b = int(color1[2] + (color2[2] - color1[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Draw abstract glassmorphic/geometric shapes
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlay)
    
    # Large abstract circles
    ol_draw.ellipse([width - 150, -50, width + 150, 250], fill=(255, 255, 255, 25))
    ol_draw.ellipse([-100, height - 200, 200, height + 100], fill=(255, 255, 255, 15))
    
    # Accent lines
    ol_draw.line([(0, 0), (width, 0)], fill=(255, 255, 255, 50), width=4)
    ol_draw.line([(0, height - 1), (width, height - 1)], fill=(0, 0, 0, 80), width=2)
    
    # Composite the shapes
    img = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(img)
    
    # Draw text
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf" # Fallback
        
    try:
        font_title = ImageFont.truetype(font_path, 40)
        font_sub = ImageFont.truetype(font_path, 18)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # Title text placement with a drop shadow
    title_text = course_name
    # Draw shadow
    draw.text((42, 182), title_text, font=font_title, fill=(0, 0, 0, 100))
    # Draw main text
    draw.text((40, 180), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Category tag placement
    draw.rounded_rectangle([40, 40, 160, 70], radius=15, fill=(255, 255, 255, 40), outline=(255, 255, 255, 80))
    draw.text((55, 45), "ADAPTLearn", font=font_sub, fill=(255, 255, 255, 220))
    
    return img.convert("RGB")

# Define courses and colors
courses = {
    "python-basics": ("Python Basics", (108, 99, 255), (0, 212, 255)),
    "django-development": ("Django Dev", (0, 230, 118), (0, 150, 136)),
    "html-fundamentals": ("HTML Fundamentals", (255, 101, 132), (255, 152, 0)),
    "css-masterclass": ("CSS Masterclass", (0, 212, 255), (33, 150, 243)),
    "javascript-essentials": ("JavaScript Essentials", (255, 215, 0), (255, 107, 53)),
    "data-structures": ("Data Structures", (103, 58, 183), (63, 81, 181)),
    "machine-learning-intro": ("Machine Learning", (233, 30, 99), (108, 99, 255)),
    "sql-basics": ("SQL Basics", (33, 150, 243), (76, 175, 80)),
    "c-programming": ("C Programming", (96, 125, 139), (38, 50, 56)),
    "java-fundamentals": ("Java Fundamentals", (255, 87, 34), (121, 85, 72))
}

os.makedirs("media/course_thumbnails", exist_ok=True)
for key, (name, c1, c2) in courses.items():
    img = draw_gradient_and_shapes(800, 450, c1, c2, name)
    img.save(f"media/course_thumbnails/{key}.png")
    print(f"Generated {key}.png")
