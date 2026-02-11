import os
import requests

GRAPH_VERSION = "v24.0"

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    file_size = os.path.getsize(video_path)
    print(f"Uploading file of size: {file_size} bytes")

    # STEP 1: START
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/video_reels"
    params = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }
    start_res = requests.post(start_url, params=params).json()
    
    if "video_id" not in start_res:
        raise Exception(f"Start failed: {start_res}")

    upload_url = start_res["upload_url"]

    # STEP 2: TRANSFER (SABSE ZARURI BADLAV)
    with open(video_path, "rb") as f:
        video_data = f.read()

    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Offset": "0",
        "Content-Length": str(len(video_data)) # Size ko string me convert kiya
    }

    # Stream=False karke direct bytes bhej rahe hain
    transfer_res = requests.post(upload_url, headers=headers, data=video_data)
    
    if transfer_res.status_code not in (200, 201):
        print(f"Status: {transfer_res.status_code}, Response: {transfer_res.text}")
        raise Exception("Video transfer failed")

    # STEP 3: FINISH
    finish_params = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": start_res["video_id"],
        "description": caption,
        "video_state": "PUBLISHED"
    }
    return requests.post(start_url, params=finish_params).json()
