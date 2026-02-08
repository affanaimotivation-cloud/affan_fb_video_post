import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration (Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Long Caption aur 20 trending hashtags ki request
        prompt = "Write 1 powerful motivational quote in HINDI. Then write a 6-line inspirational caption and 20 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "सफलता का रास्ता मेहनत से होकर गुजरता है।", "Stay motivated and keep working hard!", "#motivation #success #hindi #goals #inspiration"

def get_image_safe():
    # Retry mechanism for Pollinations AI
    for i in range(3):
        try:
            seed = random.randint(1, 999999)
            url = f"https://pollinations.ai/p/dark-professional-motivation-background?width=1080&height=1080&seed={seed}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except:
            print(f"Attempt {i+1} failed. Retrying image download...")
            time.sleep(5)
    
    # Backup Background if generator fails
    print("Using fallback solid background...")
    return Image.new('RGB', (1080, 1080), color=(15, 15, 35))

def create_image(quote):
    img = get_image_safe()
    draw = ImageDraw.Draw(img)

    # 2. Local Font Setup (Using the file you uploaded)
    try:
        # Aapne naam 'hindifont.ttf' rakha hai
        font_path = "hindifont.ttf" 
        font = ImageFont.truetype(font_path, 120) 
    except:
        print("Font file 'hindifont.ttf' nahi mili! Check your GitHub repo.")
        font = ImageFont.load_default()

    # Text wrapping logic for large font
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 12: 
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # 3. Draw Gold Text with Black Shadow
    y_text = 540 - (len(lines) * 85)
    for line in lines:
        # Shadow for readability
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        # Main Gold Text
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
    
    # Page handle at bottom
    draw.text((540, 1020), "@affan.ai.motivation", fill=(200, 200, 200), anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("Facebook API Response:", r.json())

if __name__ == "__main__":
    try:
        q, c, t = get_content()
        full_caption = f"{c}\n\n.\n.\n{t}"
        print(f"Generating post for: {q}")
        img = create_image(q)
        post_to_fb(img, full_caption)
        print("Job Successfully Completed!")
    except Exception as e:
        print(f"Final Execution Error: {e}")
