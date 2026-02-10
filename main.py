from scripts.video_create import create_video
from scripts.voiceover import create_voice
from scripts.subtitles import create_subtitles
from scripts.fb_upload import upload_video

def main():
    text = "संघर्ष ही सफलता की सबसे बड़ी सीढ़ी है।"

    video_path = create_video()
    audio_path = create_voice(text)
    subtitle_path = create_subtitles(text)

    upload_video(video_path, audio_path, subtitle_path)

if __name__ == "__main__":
    main()
