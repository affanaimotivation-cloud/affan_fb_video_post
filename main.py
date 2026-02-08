import os, requests, io, random, json, time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# आपके फिक्स ट्रेंडिंग हैशटैग्स
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # मॉडल सेटअप - टेम्परेचर 1.0 ताकि कंटेंट रिपीट न हो
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        # 'Mehnat' और 'Pehchaan' जैसे शब्दों पर पाबंदी
        prompt = f"Time:{time.time()}. Write a unique 2-line aggressive Hindi attitude quote. Don't use 'Mehnat', 'Sher', 'Pehchaan'. Use 'Sultanat', 'Daur', 'Hukumat'. Return JSON ONLY: {{\"quote\": \"...\", \"caption\": \"...\"}}"
        response = model.generate_content(prompt, generation_config={"temperature": 1.0})
        
        # JSON क्लीनिंग और लोडिंग
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        return data['quote'], data['caption']
    except:
        # बैकअप कंटेंट अगर API फेल हो
        return "पहचान की ज़रूरत उन्हें है जो भीड़ में चलते हैं, हम तो अकेले ही इतिहास लिखते हैं।", "Alpha Mindset."

def create_image(quote):
    # रैंडम इमेज फेच
    img_res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,99999)}")
    img = Image.open(io.BytesIO(img_res.content))
    
    # ब्लैक ओवरले (Text readability के लिए)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 115)
        # बड़ा वॉटरमार्क साइज 110
        w_font = ImageFont.truetype("hindifont.ttf", 110) 
    except:
        font = w_font = ImageFont.load_default()

    # टेक्स्ट रैपिंग और ड्राइंग
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
    
    # साफ़ और बड़ा वॉटरमार्क
    draw.text((540, 1015), "@affan.ai.motivation", fill=(255, 255, 255, 210), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    # फिक्स टैग्स के साथ कैप्शन
    full_caption = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
    
    img = create_image(q)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    
    # फेसबुक पर पोस्ट
    requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                  data={'message': full_caption, 'access_token': FB_ACCESS_TOKEN}, 
                  files={'source': buf.getvalue()})
    print("Post Successful with Fixed Tags!")
