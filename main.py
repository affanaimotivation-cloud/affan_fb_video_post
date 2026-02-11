import os
import time
from scripts.fb_upload import upload_video

def create_video():
    """
    यहाँ आपका वीडियो बनाने का लॉजिक आएगा।
    अभी के लिए, हम मान रहे हैं कि 'video.mp4' पहले से मौजूद है 
    या कोई दूसरी प्रोसेस इसे बना रही है।
    """
    video_file = "video.mp4" # अपनी वीडियो फाइल का नाम यहाँ लिखें
    
    if not os.path.exists(video_file):
        # अगर आप MoviePy इस्तेमाल कर रहे हैं, तो सुनिश्चित करें कि 
        # clip.write_videofile(video_file) यहाँ पूरी तरह रन हुआ हो।
        print(f"Error: {video_file} ढूंढने में असफल!")
        return None
        
    return video_file

def main():
    print("--- Process Start ---")
    
    # 1. वीडियो फाइल प्राप्त करें
    video_path = create_video()
    
    if video_path:
        # 2. वीडियो का साइज चेक करें (ताकि 111 bytes वाला एरर न आए)
        file_size = os.path.getsize(video_path)
        print(f"Video File Found: {video_path} ({file_size} bytes)")
        
        if file_size < 1000: # 1KB से छोटी फाइल मतलब वीडियो खराब है
            print("Error: वीडियो फाइल बहुत छोटी या करप्ट है। पोस्टिंग कैंसल।")
            return

        # 3. फेसबुक पर अपलोड करें
        caption = "My Awesome Reel! #motivation #reels #ai"
        try:
            print("Uploading to Facebook...")
            response = upload_video(video_path, caption)
            print("SUCCESS! Post Response:", response)
        except Exception as e:
            print(f"FAILED! Error: {str(e)}")
    
    print("--- Process End ---")

if __name__ == "__main__":
    main()
