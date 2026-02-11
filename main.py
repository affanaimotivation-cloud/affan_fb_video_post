from scripts.video_create import create_video
from scripts.fb_upload import upload_video

def main():
    # Final video create (audio + subtitles already included)
    video_path = create_video()

    caption = "🔥 Hindi Motivation Reel\nFollow @affan.ai.motivation"

    upload_video(video_path, caption)

if __name__ == "__main__":
    main()
import os

print("Video path:", video_path)
print("File exists:", os.path.exists(video_path))
print("File size:", os.path.getsize(video_path))

with open(video_path, "rb") as f:
    print("First 50 bytes:", f.read(50))
