import os
import requests
import io
import random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration (GitHub Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Instruction for Large Caption and 10+ Hashtags
        prompt = "Write 1 powerful motivational quote in HINDI. Then a long inspirational caption (4-5 lines) and 10+ trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "आज का संघर्ष कल की जीत है।", "Keep pushing forward!", "#motivation #success #hindi #goals #inspiration"

def create_image(quote):
    seed = random.randint(1, 1000000)
    # Wahi stable URL jo pehle kaam kar raha tha
    url = f"https://image.pollinations.ai/prompt/dark-professional-nature-background?width=1080&height=1080&nologo=true&seed={seed}"
    
    img_data = requests.get(url).content
    img = Image.open(io.BytesIO(img_data))
    draw = ImageDraw.Draw(img)

    # 2. Hindi Font Setup (Big Size 110)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_res = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_res), 110)
    except:
        font = ImageFont.load_default()

    # Text wrapping taaki text bada ho kar bahar na nikle
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 15:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing Text with Shadow
    y_text = 540 - (len(lines) * 60)
    for line in lines:
        draw.text((544, y_text + 4), line.strip(), fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm") # Gold Color
        y_text += 130
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("Post Response:", r.json())

if __name__ == "__main__":
    q, c, t = get_content()
    full_caption = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Job Completed Successfully!")
