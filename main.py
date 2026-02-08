import os
import requests
import io
import random
import time
import google.generativeai as genai  # Purana stable method
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Purana Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    topics = ["Empire Building", "Hard Work", "Success Habits", "Never Give Up"]
    chosen = random.choice(topics)
    try:
        # Prompt for 10-15 tags only
        prompt = f"Write a deep Hindi motivational quote about {chosen}. Then write a 10-line Hindi caption and 12 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "मेहनत का फल मीठा होता है।", "Mehnat karte raho!", "#motivation #success #viral"

def get_premium_image():
    queries = ["fitness", "success", "luxury", "mountain", "galaxy", "office"]
    q = random.choice(queries)
    try:
        seed = random.randint(1, 10000)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        # Backup stable source taaki black background na aaye
        res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,500)}")
        return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 160)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Font settings
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Bara Watermark Size 85
        watermark_font = ImageFont.truetype("hindifont.ttf", 85) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 14: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Watermark Bara Kiya
    draw.text((540, 1000), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=watermark_font, anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)

if __name__ == "__main__":
    q, c, t = get_content()
    # Handle add kiya caption mein
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Stable Post Completed!")
