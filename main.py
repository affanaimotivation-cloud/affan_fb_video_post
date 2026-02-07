import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
# Sahi model path jo 404 error nahi dega
model = genai.GenerativeModel('models/gemini-1.5-flash') 

def get_content():
    try:
        prompt = "Write 1 powerful motivational quote in HINDI. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except Exception as e:
        print(f"Gemini Fix: {e}")
        return "ख्वाब बड़े देखो, मेहनत भी बड़ी करो।", "Stay Focused!", "#motivation #hindi"

def create_image(quote):
    seed = random.randint(1, 999999)
    # Pollinations agar busy ho toh Picsum backup use hoga
    urls = [
        f"https://image.pollinations.ai/prompt/dark-nature-background?width=1080&height=1080&nologo=true&seed={seed}",
        f"https://picsum.photos/seed/{seed}/1080/1080"
    ]
    img = None
    for url in urls:
        try:
            res = requests.get(url, timeout=20)
            img = Image.open(io.BytesIO(res.content))
            break
        except: continue
    if not img: raise Exception("Image Source Failed")

    draw = ImageDraw.Draw(img)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_res = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_res), 110)
    except: font = ImageFont.load_default()

    draw.text((543, 543), quote, fill=(0, 0, 0), font=font, anchor="mm") # Shadow
    draw.text((540, 540), quote, fill=(255, 215, 0), font=font, anchor="mm") # Gold
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("Result:", r.json())

if __name__ == "__main__":
    q, c, t = get_content()
    img = create_image(q)
    post_to_fb(img, f"{c}\n\n{t}")
