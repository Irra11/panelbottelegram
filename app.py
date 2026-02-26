# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, Response
import plistlib
import uuid
import requests
import json

app = Flask(__name__)

# 🔐 CONFIGURATION
USER_BOT_TOKEN = "7159490173:AAEfsvxSCSLWiGqBCAm0uNNUEo7k11x3-UM"
# The username of your bot (without @) to redirect user back
BOT_USERNAME = "irra_esign_bot" 

@app.route('/download')
def download():
    uid = request.args.get("uid")
    if not uid:
        return "Missing Telegram User ID", 400
    return redirect(f"/api/get-profile?uid={uid}")

@app.route('/api/get-profile', methods=['GET'])
def get_profile():
    uid = request.args.get("uid", "unknown")
    # Force HTTPS for Apple profiles
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
    <string>PELLA ESIGN</string>
    <key>PayloadDisplayName</key>
    <string>Get Device UDID</string>
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
        headers={"Content-Disposition": "attachment; filename=udid.mobileconfig"}
    )

@app.route('/api/enroll', methods=['POST'])
def enroll():
    try:
        uid = request.args.get("uid")
        # Apple sends data in the body
        plist_data = plistlib.loads(request.data)
        udid = plist_data.get("UDID", "Unknown")

        if uid and udid != "Unknown":
            # Send message with a button back to the user via Bot API
            keyboard = {
                "inline_keyboard": [[
                    {"text": "✅ យល់ព្រមប្រើ UDID នេះ", "callback_data": f"set_udid_{udid}"}
                ]]
            }
            
            payload = {
                "chat_id": uid,
                "text": f"📱 **រកឃើញ UDID របស់អ្នកហើយ!**\n\n🆔 `{udid}`\n\nសូមចុចប៊ូតុងខាងក្រោមដើម្បីបន្តការទិញ៖",
                "parse_mode": "Markdown",
                "reply_markup": json.dumps(keyboard)
            }
            requests.post(f"https://api.telegram.org/bot{USER_BOT_TOKEN}/sendMessage", data=payload)

        # Redirect user back to Telegram automatically
        return redirect(f"https://t.me/{BOT_USERNAME}", code=302)

    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return "PELLA UDID API RUNNING 🚀"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
