# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import plistlib
import uuid
import requests
import json

app = Flask(__name__)

# 🔐 CONFIGURATION
USER_BOT_TOKEN = "7159490173:AAEfsvxSCSLWiGqBCAm0uNNUEo7k11x3-UM"

@app.route('/download')
def download():
    uid = request.args.get("uid")
    if not uid:
        return "Missing Telegram User ID", 400
    # Redirect to get-profile to trigger the download
    return get_profile(uid)

def get_profile(uid):
    # Manually setting the URL to ensure it is always HTTPS and correct for Render
    root_url = "https://panelbottelegram.onrender.com/"
    enroll_url = f"{root_url}api/enroll?uid={uid}"

    profile_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <dict>
        <key>URL</key>
        <string>{enroll_url}</string>
        <key>DeviceAttributes</key>
        <array>
            <string>UDID</string>
            <string>PRODUCT</string>
            <string>VERSION</string>
        </array>
    </dict>
    <key>PayloadOrganization</key>
    <string>Pella Esign</string>
    <key>PayloadDisplayName</key>
    <string>Pella UDID Auto-Installer</string>
    <key>PayloadIdentifier</key>
    <string>com.pella.udid.{uuid.uuid4()}</string>
    <key>PayloadUUID</key>
    <string>{uuid.uuid4()}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>PayloadType</key>
    <string>Profile Service</string>
</dict>
</plist>"""

    return Response(
        profile_xml,
        mimetype="application/x-apple-aspen-config",
        headers={"Content-Disposition": "attachment; filename=pella_udid.mobileconfig"}
    )

@app.route('/api/enroll', methods=['POST'])
def enroll():
    try:
        uid = request.args.get("uid")
        # Apple sends the UDID in the request.data (Binary Plist)
        plist_data = plistlib.loads(request.data)
        udid = plist_data.get("UDID", "Unknown")

        if uid and udid != "Unknown":
            # Send message with button to the bot
            keyboard = {
                "inline_keyboard": [[
                    {"text": "✅ Click to Confirm UDID", "callback_data": f"set_udid_{udid}"}
                ]]
            }
            
            payload = {
                "chat_id": uid,
                "text": f"📱 **រកឃើញ UDID របស់អ្នកហើយ!**\n\n🆔 `{udid}`\n\nសូមត្រលប់មក Telegram វិញរួចចុចប៊ូតុងខាងក្រោម៖",
                "parse_mode": "Markdown",
                "reply_markup": json.dumps(keyboard)
            }
            
            requests.post(f"https://api.telegram.org/bot{USER_BOT_TOKEN}/sendMessage", data=payload)

        # IMPORTANT: Return 200 OK so the iPhone shows "Profile Installed"
        # DO NOT REDIRECT HERE
        return Response("Success", status=200)

    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

@app.route('/')
def home():
    return "Pella UDID API is Online 🚀"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000) # Render usually uses port 10000
