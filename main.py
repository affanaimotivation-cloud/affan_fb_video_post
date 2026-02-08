import os, requests, io, random, json, time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 1. Setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Aapke trending hashtags jo hamesha aayenge
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_fresh_content():
    # Temperature 1.0 taaki har baar naya content mile
    try:
        prompt = f"Time:{time.time()}. Task: Write a brand new 2-line savage Hindi attitude quote. Use heavy words like 'Sultanat', 'Daur', 'Hukumat'. STRICT: No 'Mehnat', 'Pehchaan', 'Sher'. Return JSON: {{\"quote\": \"...\", \"caption\": \"...\"}}"
        response = client.models.generate_content(model="gemini-1.5-flash", config={'temperature': 1.0}, contents=prompt)
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except:
        return "अपना दौर खुद बनाओ, दुनिया तो नकल करने में माहिर है।", "The Alpha King."

def create_image(quote):
    # Dynamic Image
    img_data = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,9999)}").content
    img = Image.open(io.BytesIO(img_data))
    
    # Black Overlay taaki text saaf dikhe
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 180))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 115)
        w_font = ImageFont.truetype("hindifont.ttf", 110) # Bada Watermark
    except:
        font = w_font = ImageFont.load_default()

    # Simple Text Wrap & Draw
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 14: current += w + " "
        else: lines.append(current); current = w + " "
    lines.append(current)

    y = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((540, y), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y += 180
    
    # Large Clear Watermark
    draw.text((540, 1000), "@affan.ai.motivation", fill=(255, 255, 255, 210), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_fresh_content()
    full_caption = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
    
    img = create_image(q)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    
    # Facebook Post
    requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                  data={'message': full_caption, 'access_token': FB_ACCESS_TOKEN}, 
                  files={'source': buf.getvalue()})
    print("Success: Fresh Content Posted!")
