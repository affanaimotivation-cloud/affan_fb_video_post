import os
import requests
from gtts import gTTS
from dotenv import load_dotenv
import subprocess

load_dotenv()

GRAPH_VERSION = "v24.0"

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


# ---------------------------
# 1️⃣ Download Free Video
# ---------------------------
def download_video():
    url = "https://api.pexels.com/videos/search?query=nature&per_page=1"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    res = requests.get(url, headers=headers).json()
    video_url = res["videos"][0]["video_files"][0]["link"]

    r = requests.get(video_url, stream=True)

    with open("video.mp4", "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print("Video Downloaded:", os.path.getsize("video.mp4"))


# ---------------------------
# 2️⃣ Generate Hindi Motivation Voice (Updated to 5 Lines)
# ---------------------------
def generate_voice():
    # Yeh rahi aapki 5 line ki motivational quote
    text = """
    मंजिल उन्हीं को मिलती है जिनके सपनों में जान होती है,
    पंखों से कुछ नहीं होता हौसलों से उड़ान होती है।
    मैदान में हारा हुआ इंसान फिर से जीत सकता है,
    लेकिन मन से हारा हुआ इंसान कभी नहीं जीत सकता।
    इसलिए अपने मन को मजबूत बनाओ और आगे बढ़ो।
    """

    tts = gTTS(text=text, lang="hi")
    tts.save("voice.mp3")
    print("Voice Generated (5 Lines)")


# ---------------------------
# 3️⃣ Merge Video + Voice
# ---------------------------
def merge_video():
    command = [
        "ffmpeg",
        "-y",
        "-i", "video.mp4",
        "-i", "voice.mp3",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "final_video.mp4"
    ]

    subprocess.run(command)
    print("Video Merged:", os.path.getsize("final_video.mp4"))


# ---------------------------
# 4️⃣ Upload to Facebook
# ---------------------------
def upload_video(video_path, caption=""):
    file_size = os.path.getsize(video_path)

    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{FB_PAGE_ID}/video_reels"

    start_payload = {
        "access_token": FB_PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }

    start_res = requests.post(start_url, data=start_payload).json()
    
    if "video_id" not in start_res:
        print("Error starting upload:", start_res)
        return

    video_id = start_res["video_id"]
    upload_url = start_res["upload_url"]

    headers = {
        "Authorization": f"OAuth {FB_PAGE_TOKEN}",
        "Offset": "0",
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as f:
        transfer = requests.post(upload_url, headers=headers, data=f)

    if transfer.status_code not in (200, 201):
        raise Exception("Transfer failed")

    finish_payload = {
        "access_token": FB_PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption,
        "video_state": "PUBLISHED"
    }

    finish_res = requests.post(start_url, data=finish_payload)
    print("Upload Done:", finish_res.json())


# ---------------------------
# MAIN RUN
# ---------------------------
def main():
    try:
        download_video()
        generate_voice()
        merge_video()
        upload_video("final_video.mp4", "सफलता का मंत्र 💪 #motivation #hindi #reels")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
