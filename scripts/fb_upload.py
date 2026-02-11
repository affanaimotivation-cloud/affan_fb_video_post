import os
import requests

GRAPH_VERSION = "v24.0"


def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID or FB_PAGE_TOKEN missing")

    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found")

    print("Uploading normal video...")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/videos"

    files = {
        "source": open(video_path, "rb")
    }

    data = {
        "access_token": PAGE_TOKEN,
        "description": caption
    }

    response = requests.post(url, files=files, data=data)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    if response.status_code != 200:
        raise Exception("Video upload failed")

    print("✅ Video Uploaded Successfully!")
    return response.json()
