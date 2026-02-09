import os, requests, io, random, json, time
from google import genai  # Nayi library import
from PIL import Image, ImageDraw, ImageFont

# 1. API Client Setup using Secrets
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Trending Hashtags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_unique_content():
    """Gemini se fresh content lane ke liye"""
    try:
        # Unique timestamp taaki repetition na ho
        prompt = (f"Time:{time.time()}. Task: Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Duniya', 'Andaz'. "
                  "Focus on: Royal, Power, Empire. "
                  "Return JSON ONLY: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        # FIX: Sahi model name jo 404 nahi dega
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={'temperature': 1.0}, 
            contents=prompt
        )
        
        # Clean JSON parsing logic
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        data = json.loads(raw_text)
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Content Error (404/API): {e}")
        return None, None

def create_image(quote):
    """Image generation and text wrapping logic"""
    # Random HD background
    img_res = requests.get(f"[https://picsum.photos/1080/1080?random=](https://picsum.photos/1080/1080?random=){random.random()}")
    img = Image.open(io.BytesIO(img_res.content))
    
    # Dark Overlay for visibility
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 195))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Font size 80 for safety
        font = ImageFont.truetype("hindifont.ttf", 80)
        w_font = ImageFont.truetype("hindifont.ttf", 100) 
    except:
        font = w_font = ImageFont.load_default()

    # Wrap text logic (Max 18 chars per line)
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 18: current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    lines.append(current.strip())

    # Vertical Centering
    y = (1080 - (len(lines) * 115)) // 2 
    for line in lines:
        # Shadow effect and Golden main text
        draw.text((543, y + 3), line, fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm")
        y += 115
    
    # Branded Watermark
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 170), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    quote, caption = get_unique_content()
    
    if quote and caption:
        full_cap = f"{caption}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        final_img = create_image(quote)
        
        # Buffer for Facebook Upload
        buf = io.BytesIO()
        final_img.save(buf, format='JPEG', quality=95)
        
        # Post to FB Page
        res = requests.post(f"[https://graph.facebook.com/](https://graph.facebook.com/){FB_PAGE_ID}/photos", 
                            data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                            files={'source': buf.getvalue()})
        
        if res.status_code == 200:
            print("Post successful!")
        else:
            print(f"Post failed: {res.text}")
    else:
        print("Skipped due to API/Model error.")
