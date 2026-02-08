import os, requests, io, random, json, time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Aapke fixed trending hashtags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # Dynamic prompt taaki content kabhi repeat na ho
    try:
        t_stamp = time.time()
        prompt = (f"ID:{t_stamp}. Task: Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Sher', 'Khamoshi'. "
                  "Use aggressive words like 'Hukumat', 'Khauf', 'Badshah'. "
                  "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        response = client.models.generate_content(model="gemini-1.5-flash", config={'temperature': 1.0}, contents=prompt)
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except:
        return "अपना राज है, अपना अंदाज़ है, जो जलते हैं जलने दो।", "Living like a king."

def create_image(quote):
    # Image fetching
    img = Image.open(io.BytesIO(requests.get(f"https://picsum.photos/1080/1080?random={random.random()}").content))
    
    # Black Overlay (Transparent)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 170))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Font size thoda chota kiya taaki bahar na jaye
        font = ImageFont.truetype("hindifont.ttf", 95)
        w_font = ImageFont.truetype("hindifont.ttf", 80) # Watermark size
    except:
        font = w_font = ImageFont.load_default()

    # Dynamic Text Wrap: Ek line mein sirf 12-14 characters
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 15: current += w + " "
        else: lines.append(current.strip()); current = w + " "
    lines.append(current.strip())

    # Auto-Centering: Gap ko lines ke hisaab se adjust kiya (95 ki jagah 130 step)
    total_h = len(lines) * 130
    y = (1080 - total_h) // 2 
    
    for line in lines:
        # Text shadow for clarity
        draw.text((544, y + 4), line, fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm")
        y += 130 # Gap kam kiya taaki image ke andar rahe
    
    # Large Watermark
    draw.text((540, 1000), "@affan.ai.motivation", fill=(255, 255, 255, 200), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    full_cap = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
    
    img = create_image(q)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    
    # FB Post
    requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                  data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                  files={'source': buf.getvalue()})
    print("Run Success: Text wrap fixed & Fresh Content Postively Posted!")
