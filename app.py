# -*- coding: utf-8 -*-
from flask import Flask, request, Response, redirect
import plistlib
import uuid
import requests
import json

app = Flask(__name__)

# 🔐 CONFIGURATION
USER_BOT_TOKEN = "7159490173:AAEfsvxSCSLWiGqBCAm0uNNUEo7k11x3-UM"
BOT_USERNAME = "Irra_EsignBot" # Your Bot Username without @

@app.route('/download')
def download():
    uid = request.args.get("uid")
    if not uid:
        return "Missing Telegram User ID", 400
    
    root_url = "https://panelbottelegram.onrender.com/"
    enroll_url = f"{root_url}api/enroll?uid={uid}"

    # Generate the Apple Profile
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
    <string>Irra Esign</string>
    <key>PayloadDisplayName</key>
    <string>Irra Esign UDID Auto-Installer</string>
    <key>PayloadIdentifier</key>
    <string>com.irra.udid.{uuid.uuid4()}</string>
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
        headers={"Content-Disposition": "attachment; filename=irra.mobileconfig"}
    )

@app.route('/api/enroll', methods=['POST'])
def enroll():
    try:
        uid = request.args.get("uid")
        # Extract UDID from Apple's binary plist data
        plist_data = plistlib.loads(request.data)
        udid = plist_data.get("UDID", "Unknown")

        if uid and udid != "Unknown":
            # Bot sends message to user with the confirmation button
            keyboard = {
                "inline_keyboard": [[
                    {"text": "✅ យល់ព្រមប្រើ UDID នេះ", "callback_data": f"set_udid_{udid}"}
                ]]
            }
            payload = {
                "chat_id": uid,
                "text": f"📱 **ទទួលបាន UDID រួចរាល់!**\n\n🆔 UDID: `{udid}`\n\nសូមចុចប៊ូតុងខាងក្រោមដើម្បីបន្ត៖",
                "parse_mode": "Markdown",
                "reply_markup": json.dumps(keyboard)
            }
            requests.post(f"https://api.telegram.org/bot{USER_BOT_TOKEN}/sendMessage", data=payload)

        # ✅ CRITICAL: Use 301 Redirect to the Success Page
        # This prevents the "Connection Failed" error and opens Safari
        return redirect("https://panelbottelegram.onrender.com/success", code=301)

    except Exception:
        return Response(status=500)

@app.route('/success')
def success():
    # This page uses JavaScript to force-open the Telegram App
    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Returning to Telegram...</title>
        <script>
            // Deep link to open the bot in the Telegram App
            window.location.href = "tg://resolve?domain={BOT_USERNAME}";
            // Fallback: If it doesn't open in 1 second, show the manual link
            setTimeout(function() {{
                window.location.href = "https://t.me/{BOT_USERNAME}";
            }}, 1000);
        </script>
    </head>
    <body style="text-align:center; font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding-top:100px;">
        <h2 style="color: #333;">✅ UDID ទទួលបានជោគជ័យ!</h2>
        <p style="color: #666;">កំពុងនាំអ្នកត្រលប់ទៅ Telegram វិញ...</p>
        <br>
        <a href="tg://resolve?domain={BOT_USERNAME}" 
           style="background-color: #0088cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">
           ចុចទីនេះដើម្បីត្រលប់ទៅ Bot
        </a>
    </body>
    </html>
    """
    return html

@app.route('/')
def home():
    return "Irra Esign API is Live 🚀"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
