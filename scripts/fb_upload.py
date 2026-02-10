# ---------------- STEP 2: TRANSFER ----------------
upload_url = upload_url.strip("[]")  # markdown issue fix

with open(video_path, "rb") as f:
    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Content-Type": "application/octet-stream",
        "file_offset": "0"
    }

    transfer_res = requests.post(
        upload_url,
        headers=headers,
        data=f
    )

print("TRANSFER STATUS:", transfer_res.status_code)
print("TRANSFER RESPONSE:", transfer_res.text)

if transfer_res.status_code not in (200, 201):
    raise Exception("Video transfer failed")
