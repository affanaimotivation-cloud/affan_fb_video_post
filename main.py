import os
import requests
import io
import random
import json
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

def get_content():
    # Diversified topics to break the "Hard Work" loop
    topics = ["Savage Attitude", "Dark Power", "Luxury Empire", "Quiet Revenge", "Stoic King", "Unstoppable Ego"]
    chosen = random.choice(topics)
    # Using float timestamp to force Gemini to rethink every second
    unique_id = time.time()
    
    # Temperature high (1.0) for maximum randomness
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 1.0})
    
    try:
        # Explicitly banning the word 'Mehnat' and 'Hardwork'
        prompt = (
            f"ID: {unique_id}. Topic: {chosen}. "
            "Task: Write a deep, aggressive Hindi quote (Shayari style). "
            "STRICT RULE: Do NOT use common words like 'Mehnat', 'Hard work', 'Safalta'. Use 'Zamana', 'Aukaat', 'Raaj', 'Khaamoshi'. "
            "Write a 10-line caption and exactly 15 trending hashtags. "
            "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\", \"tags\": \"#...\"}"
        )
        response = model.generate_content(prompt)
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption'], data['tags']
    except:
        return "शेर जब खामोश होता है, तो पूरा जंगल कांपता है।", "Silence is power.", "#attitude #king #power #stoic #luxury"

def get_premium_image():
    # Dynamic seed to prevent black or repeat backgrounds
    seed = random.randint(1, 1000000)
    url = f"https://picsum.photos/1080/1080?random={seed}"
    res = requests.get(url, timeout=30)
    return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 175)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Super-sized fonts for impact
        font = ImageFont.truetype("hindifont.ttf", 115)
        watermark_font = ImageFont.truetype("hindifont.ttf", 100) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else:
            lines.append(current_line); current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), (0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), (255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Large watermark (Size 100)
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 210), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c, t = get_content()
    # Adding follow handle to every post
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    
    img = create_image(q)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    
    # Direct Post
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': full_caption, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)
    print("Unique High-Quality Content Posted!")
