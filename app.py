import os
import re
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔴 CHANGE THIS to the URL where your HTML is hosted
FRONTEND_URL = "https://your-website-domain.com/"

@app.route('/api/get-profile')
def get_profile():
    # Detect the current server URL for enrollment
    root_url = request.url_root.replace("http://", "https://")
    enroll_url = f"{root_url}api/enroll"
    
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
    <string>Irra Store</string>
    <key>PayloadDisplayName</key>
    <string>Device UDID Fetcher</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>PayloadUUID</key>
    <string>{uuid.uuid4()}</string>
    <key>PayloadIdentifier</key>
    <string>com.irra.udid</string>
    <key>PayloadType</key>
    <string>Profile Service</string>
</dict>
</plist>"""
    return profile_xml, 200, {'Content-Type': 'application/x-apple-aspen-config'}

@app.route('/api/enroll', methods=['POST'])
def enroll():
    # Extract UDID from the binary request sent by iOS
    raw_data = request.get_data().decode('latin-1')
    udid_match = re.search(r'<key>UDID</key>\s*<string>(.*?)</string>', raw_data)
    
    if udid_match:
        udid = udid_match.group(1)
        # Redirect back to your website with the UDID in the URL
        return "", 301, {'Location': f"{FRONTEND_URL}?udid={udid}"}
    
    return "Extraction Failed", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
