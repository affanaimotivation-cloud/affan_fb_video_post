import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    # Topics ki list ko bada kiya taaki repeat na ho
    topics = [
        "Unstoppable Discipline", "Morning Energy", "Financial Freedom", 
        "Handling Stress", "Power of Silence", "Growth Mindset", 
        "Winning Alone", "Body Language", "Confidence"
    ]
    chosen = random.choice(topics)
    
    # Har baar unique result ke liye current time ko seed ki tarah use kiya
    current_time = time.strftime("%H:%M:%S")
    
    try:
        # Prompt mein temperature aur uniqueness add karne ke liye instructions badle hain
        prompt = f"Topic: {chosen}. Time Context: {current_time}. Write a unique, powerful 2-line motivational quote in HINDI. Then write a 12-line deep inspirational caption and 40 trending hashtags. Format: Quote | Caption | Tags. IMPORTANT: Do not use the word 'Khwaab' or 'Sapne' every time."
        
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        else:
            raise ValueError("Incomplete response from AI")
            
    except Exception as e:
        print(f"Error fetching new content: {e}")
        # Default backup ko bhi random bana diya taaki black background jaisa feel na aaye
        backups = [
            ("संघर्ष ही जीवन की असली कहानी है।", "Hausla mat haro!", "#motivation #hindi"),
            ("वक्त बदलता है, बस मेहनत जारी रखो।", "Aage badhte raho!", "#success #viral"),
            ("खुद पर विश्वास रखो, सब संभव है।", "Believe in yourself!", "#inspiration #goals")
        ]
        res = random.choice(backups)
        return res[0], res[1], res[2]

def get_premium_image():
    queries = ["entrepreneur", "success", "fitness", "luxury", "dark-nature", "city-night", "working-man"]
    q = random.choice(queries)
    try:
        # Sig parameter ko bada kiya taaki image hamesha alag aaye
        seed = random.randint(1, 99999)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        return Image.open(io.BytesIO(res.content))
    except:
        url = f"https://picsum.photos/1080/1080?random={random.randint(1,1000)}"
        res = requests.get(url)
        return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 160)) # Thoda dark overlay for clarity
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("hindifont.ttf", 110) 
    except:
        font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
    
    # Niche aapka handle
    draw.text((540, 1030), "@affan.ai.motivation", fill=(255, 255, 255), anchor="mm")
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
    full_cap = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_cap)
    print(f"Post Done! Topic was: {q[:20]}...")
