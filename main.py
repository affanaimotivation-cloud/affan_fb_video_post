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

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        prompt = "Write 1 short powerful motivational quote. Just the text, no quotes."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except:
        return "Your limitation—it's only your imagination."

def create_image(quote):
    # Stable Image Source: Unsplash Source or Picsum
    for i in range(3):
        try:
            seed = random.randint(1, 1000)
            # Hum Picsum use karenge jo bahut stable hai
            img_url = f"https://picsum.photos/seed/{seed}/1080/1080?blur=2"
            
            response = requests.get(img_url, timeout=30)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                # Image ko thoda dark karenge taaki text dikhe
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay).convert('RGB')
                
                draw = ImageDraw.Draw(img)
                # Default font ke sath text center mein
                draw.text((540, 540), quote, fill=(255, 255, 255), anchor="mm")
                return img
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None

def post_to_fb(image_obj, message):
    if image_obj is None: return
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    
    r = requests.post(url, data=payload, files=files)
    print("FACEBOOK RESPONSE:", r.json())

if __name__ == "__main__":
    q = get_content()
    print(f"Quote: {q}")
    img = create_image(q)
    if img:
        post_to_fb(img, q)
        print("Done!")
    else:
        print("Could not get image.")
