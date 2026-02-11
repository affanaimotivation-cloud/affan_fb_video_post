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

    file_size = os.path.getsize(video_path)

    if file_size < 1000:
        raise ValueError("Video file too small or invalid")

    print("Uploading file size:", file_size)

    # =====================================
    # STEP 1️⃣ START
    # =====================================
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/videos"


    start_payload = {
        "upload_phase": "start",
        "file_size": file_size,
        "access_token": PAGE_TOKEN
    }

    start_res = requests.post(start_url, data=start_payload)
    start_data = start_res.json()

    print("START STATUS:", start_res.status_code)
    print("START RESPONSE:", start_data)

    if start_res.status_code != 200:
        raise Exception("Start phase failed")

    video_id = start_data["video_id"]
    upload_url = start_data["upload_url"]

    # =====================================
    # STEP 2️⃣ TRANSFER (Single clean binary)
    # =====================================
    with open(video_path, "rb") as f:
        video_binary = f.read()

    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Content-Type": "application/octet-stream"
    }

    transfer_res = requests.post(
        upload_url,
        headers=headers,
        data=video_binary
    )

    print("TRANSFER STATUS:", transfer_res.status_code)
    print("TRANSFER RESPONSE:", transfer_res.text)

    if transfer_res.status_code not in (200, 201):
        raise Exception("Transfer phase failed")

    # =====================================
    # STEP 3️⃣ FINISH
    # =====================================
    finish_payload = {
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption,
        "video_state": "PUBLISHED",
        "access_token": PAGE_TOKEN
    }

    finish_res = requests.post(start_url, data=finish_payload)
    finish_data = finish_res.json()

    print("FINISH STATUS:", finish_res.status_code)
    print("FINISH RESPONSE:", finish_data)

    if finish_res.status_code != 200:
        raise Exception("Finish phase failed")

    print("✅ Reel Uploaded Successfully!")
    return finish_data
