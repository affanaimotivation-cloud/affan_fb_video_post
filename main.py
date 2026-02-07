import os
import requests
import io
import random
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
        # Gemini se Hindi Quote aur Hashtags maangna
        prompt = "Write 1 powerful motivational quote in HINDI. Then provide a caption and 5 trending hashtags. Format: Quote | Caption | Hashtags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "सफलता की शुरुआत कोशिश से होती है।", "Keep Pushing!", "#motivation #hindi #success"

def get_font():
    # Hindi support ke liye Google Font download karna
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
    r = requests.get(font_url)
    return io.BytesIO(r.content)

def create_image(quote):
    seed = random.randint(1, 999999)
    img_url = f"https://image.pollinations.ai/prompt/dark-motivational-background?width=1080&height=1080&nologo=true&seed={seed}"
    img = Image.open(io.BytesIO(requests.get(img_url).content))
    draw = ImageDraw.Draw(img)
    
    # Font size 80 (Bada text)
    try:
        font_data = get_font()
        font = ImageFont.truetype(font_data, 80)
    except:
        font = ImageFont.load_default()

    # Text ko wrap karna aur center mein daalna
    w, h = 1080, 1080
    draw.text((w/2, h/2), quote, fill=(255, 255, 255), font=font, anchor="mm", align="center")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    # Caption aur Hashtags 'message' mein jayenge
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("FB Response:", r.json())

if __name__ == "__main__":
    quote, caption, tags = get_content()
    full_message = f"{caption}\n\n{tags}"
    print(f"Post Content: {quote}")
    
    img = create_image(quote)
    post_to_fb(img, full_message)
