import os
import requests
import io
import random
import time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY)

def get_content():
    topics = ["Empire Building", "Mental Toughness", "Zero Distractions", "Success Habits", "King Mindset"]
    chosen = random.choice(topics)
    try:
        # Instruction for 10-15 hashtags only
        prompt = f"Topic: {chosen}. Task: 1. Write a deep Hindi motivational quote. 2. Write a 10-line Hindi caption. 3. Provide between 10 to 15 highly relevant trending hashtags starting with #. Format exactly like this: QUOTE_START (quote) QUOTE_END CAPTION_START (caption) CAPTION_END TAGS_START (tags) TAGS_END"
        
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        text = response.text
        
        q = text.split("QUOTE_START")[1].split("QUOTE_END")[0].strip()
        c = text.split("CAPTION_START")[1].split("CAPTION_END")[0].strip()
        t = text.split("TAGS_START")[1].split("TAGS_END")[0].strip()
        
        return q, c, t
    except:
        return "वक्त बदलta है, बस मेहनत जारी रखो।", "Mehnat hi safalta ki chabi hai.", "#motivation #success #viral #trending #mindset #goals"

def get_premium_image():
    queries = ["fitness-bodybuilder", "luxury-office", "supercar", "dark-galaxy", "mountain-summit", "rich-lifestyle"]
    q = random.choice(queries)
    try:
        seed = random.randint(1, 20000)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,999)}")
        return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 165)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("hindifont.ttf", 115)
        # Watermark size 80 (Bara size)
        watermark_font = ImageFont.truetype("hindifont.ttf", 80) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 195
    
    # Large watermark at bottom
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
    # Adding follow handle in caption
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Success: 10-15 Tags & Large Watermark Posted!")
