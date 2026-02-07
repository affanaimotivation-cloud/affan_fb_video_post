import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        prompt = "Write 1 short powerful motivational quote. Just the text, no quotes."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except:
        return "Push yourself, because no one else is going to do it for you."

def create_image(quote):
    # Try different styles if one fails
    styles = ["nature", "dark-abstract", "motivational-office", "galaxy"]
    
    for i in range(3):
        try:
            seed = random.randint(1, 999999)
            style = random.choice(styles)
            # Naya aur zyada stable URL format
            img_url = f"https://pollinations.ai/p/{style}-background-for-quotes?width=1080&height=1080&seed={seed}"
            
            # Browser jaisa behavior dikhane ke liye headers
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(img_url, headers=headers, timeout=40)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                draw = ImageDraw.Draw(img)
                # Drawing simple text in center
                draw.text((540, 540), quote, fill=(255, 255, 255), anchor="mm")
                return img
        except Exception as e:
            print(f"Image Attempt {i+1} Error: {e}")
            time.sleep(3)
    return None

def post_to_fb(image_obj, message):
    if image_obj is None: return
    
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=85)
    
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    
    r = requests.post(url, data=payload, files=files)
    print("FACEBOOK SAYS:", r.json())

if __name__ == "__main__":
    q = get_content()
    print(f"Quote: {q}")
    img = create_image(q)
    if img:
        post_to_fb(img, q)
    else:
        print("Final Error: Image server not responding. Re-run once more.")
