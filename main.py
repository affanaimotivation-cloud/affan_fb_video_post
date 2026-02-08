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

# 2. Permanent Trending Hashtags (Ye hamesha aayenge)
DEFAULT_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude"

def get_content():
    unique_seed = random.randint(1, 999999)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 1.0})
    
    try:
        # Gemini ko instruction ki sirf 5 naye tags de
        prompt = (
            f"Seed: {unique_seed}. Task: Write a brand new 2-line aggressive Hindi attitude quote. "
            "STRICT RULE: Do NOT use 'Mehnat', 'Sher', or 'Khamoshi'. Use words like 'Sultanat', 'Baaz', 'Tufan'. "
            "Provide a 10-line caption and 5 unique trending hashtags. "
            "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\", \"tags\": \"#...\"}"
        )
        response = model.generate_content(prompt)
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption'], data['tags']
    except:
        return "पहचान ऐसी कि दुनिया देखती रह जाए।", "Build your legacy.", "#power #alpha #money"

def create_image(quote):
    # Image fetching from stable source
    url = f"https://picsum.photos/1080/1080?random={random.randint(1,100000)}"
    res = requests.get(url, timeout=30)
    img = Image.open(io.BytesIO(res.content))
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 175)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 115)
        # Bada Watermark Size 110
        watermark_font = ImageFont.truetype("hindifont.ttf", 70) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Quote wrap logic
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
    
    # Bada Watermark
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 210), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c, t = get_content()
    # Fixed Default Tags + Gemini Tags
    final_tags = f"{DEFAULT_TAGS} {t}"
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{final_tags}"
    
    img = create_image(q)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    
    # Facebook Post logic
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': full_caption, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)
    print("Success: Fixed Tags & Fresh Content Posted!")
