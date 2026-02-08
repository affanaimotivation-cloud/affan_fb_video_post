import os, requests, io, random, json, time
# Naya import tareeka taaki 'ImportError' na aaye
from google import genai 
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
# Naya Client format
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Aapke fixed trending hashtags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    try:
        # Unique seed taaki repeat na ho
        prompt = f"Time:{time.time()}. Write a new 2-line savage Hindi attitude quote. No 'Mehnat', No 'Pehchaan'. Use 'Sultanat', 'Daur'. Return JSON: {{\"quote\": \"...\", \"caption\": \"...\"}}"
        
        # Naya model calling method
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt,
            config={'temperature': 1.0}
        )
        
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except Exception as e:
        print(f"API Error: {e}")
        return "दौर शुरू हो चुका है, अब सिर्फ़ तबाही मचेगी।", "The Era Begins."

def create_image(quote):
    # Dynamic Image fetch
    img_res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,99999)}")
    img = Image.open(io.BytesIO(img_res.content))
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 115)
        w_font = ImageFont.truetype("hindifont.ttf", 110) # Bada Watermark
    except:
        font = w_font = ImageFont.load_default()

    # Text wrapping
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 13: current += w + " "
        else: lines.append(current); current = w + " "
    lines.append(current)

    y = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((540, y), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y += 195
    
    # Large Watermark
    draw.text((540, 1015), "@affan.ai.motivation", fill=(255, 255, 255, 210), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    full_caption = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
    
    img = create_image(q)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    
    # Facebook post
    requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                  data={'message': full_caption, 'access_token': FB_ACCESS_TOKEN}, 
                  files={'source': buf.getvalue()})
    print("Task Done with latest Library!")
