import os
import requests
import io
import random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Using your exact Secret names)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        prompt = "Write 1 powerful short motivational quote. Result should be just the quote text."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Believe in yourself and the world will believe in you."

def create_image(quote):
    # Image from Pollinations AI (Fast & Free)
    seed = random.randint(1, 999999)
    img_url = f"https://image.pollinations.ai/prompt/dark-professional-motivation-background?width=1080&height=1080&nologo=true&seed={seed}"
    
    img_data = requests.get(img_url).content
    img = Image.open(io.BytesIO(img_data))
    draw = ImageDraw.Draw(img)
    
    # Simple centered text
    # Default font size is small, but works without extra files
    draw.text((540, 540), quote, fill=(255, 255, 255), anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    
    r = requests.post(url, data=payload, files=files)
    print("FB Response:", r.json())

# Final Execution
if __name__ == "__main__":
    try:
        final_quote = get_content()
        print(f"Quote Generated: {final_quote}")
        
        final_img = create_image(final_quote)
        print("Image Created.")
        
        post_to_fb(final_img, final_quote)
        print("Process Finished.")
    except Exception as e:
        print(f"Execution Error: {e}")
