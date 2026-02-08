import os
import requests
import io
import random
import json
import time
from google import genai # Nayi Library
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Naya Connection Method
client = genai.Client(api_key=GEMINI_KEY)

# Trending Tags Fix
DEFAULT_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # Content ko bilkul fresh rakha hai
    try:
        prompt = (
            "Write a brand new aggressive Hindi attitude quote. "
            "STRICT RULES: Do NOT use 'Mehnat', 'Pehchaan', 'Sher', or 'Khamoshi'. "
            "Use words like 'Sultanat', 'Dahshat', 'Aukaat', 'Khel', 'Badshah'. "
            "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}"
        )
        
        # Naya Model Call
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def create_image(quote):
    # Background Image
    res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,99999)}")
    img = Image.open(io.BytesIO(res.content))
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 112)
        # Bada Watermark Size 110
        watermark_font = ImageFont.truetype("hindifont.ttf", 70) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Wrap Text
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else: lines.append(current_line); current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), (0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), (255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Large Watermark
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 215), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    if q and c:
        full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{DEFAULT_TAGS}"
        img = create_image(q)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        
        # FB Post
        requests.post(
            f"https://graph.facebook.com/{FB_PAGE_ID}/photos",
            data={'message': full_caption, 'access_token': FB_ACCESS_TOKEN},
            files={'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        )
        print("Final Success with New Library!")
