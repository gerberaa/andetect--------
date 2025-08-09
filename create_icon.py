#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Створення простої іконки для AnDetect Profile Manager
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_simple_icon():
    """Створення простої іконки"""
    if not PIL_AVAILABLE:
        print("⚠️  PIL не встановлено. Створюю іконку без зображення.")
        return False
    
    # Створюємо зображення 256x256
    img = Image.new('RGBA', (256, 256), (26, 35, 126, 255))  # Синій фон
    draw = ImageDraw.Draw(img)
    
    # Малюємо простий дизайн
    # Зовнішнє коло
    draw.ellipse([20, 20, 236, 236], fill=(255, 255, 255, 255))
    
    # Внутрішнє коло
    draw.ellipse([40, 40, 216, 216], fill=(26, 35, 126, 255))
    
    # Буква A
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    # Центруємо текст
    bbox = draw.textbbox((0, 0), "A", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10
    
    draw.text((x, y), "A", fill=(255, 255, 255, 255), font=font)
    
    # Зберігаємо як ICO
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("✅ Іконку створено: icon.ico")
    return True

def create_text_icon():
    """Створення текстової іконки якщо PIL недоступний"""
    # Створюємо просту .ico заглушку
    ico_content = b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00'
    
    with open('icon.ico', 'wb') as f:
        f.write(ico_content + b'\x00' * (1000 - len(ico_content)))
    
    print("✅ Базову іконку створено: icon.ico")

if __name__ == "__main__":
    if not create_simple_icon():
        create_text_icon()
