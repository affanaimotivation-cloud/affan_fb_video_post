def get_unique_content():
    try:
        prompt = (f"Time:{time.time()}. Task: Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Duniya', 'Andaz'. "
                  "Focus on: Royal, Power, Empire. "
                  "Return JSON ONLY: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        # FIX: Model ka pura naam 'models/gemini-1.5-flash' use karein
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={
                'temperature': 1.0,
                # Explicitly setting model version if needed
            }, 
            contents=prompt
        )
        
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        data = json.loads(raw_text)
        return data['quote'], data['caption']
    except Exception as e:
        # Agar 404 phir bhi aaye, toh 'gemini-1.5-flash' ki jagah 'gemini-1.5-flash-8b' try karein
        print(f"Content Generation Error: {e}")
        return None, None
