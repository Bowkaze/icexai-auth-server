from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import hashlib
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Sử dụng biến môi trường hoặc file local
KEYS_FILE = os.getenv('KEYS_FILE', 'keys.json')

def load_keys():
    """Load keys từ file JSON"""
    if not os.path.exists(KEYS_FILE):
        return []
    try:
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_keys(data):
    """Lưu keys vào file JSON"""
    try:
        with open(KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")
        return False

def get_hwid_hash(hwid):
    """Hash HWID để bảo mật"""
    return hashlib.sha256(hwid.encode()).hexdigest()[:16]

def check_expiry(key_data):
    """Kiểm tra key có hết hạn không"""
    if 'expire_at' in key_data:
        try:
            expire = datetime.strptime(key_data['expire_at'], "%Y-%m-%d %H:%M:%S")
            return datetime.now() > expire
        except:
            pass
    if 'expiry' in key_data and key_data['expiry'] != 0:
        return time.time() > key_data['expiry']
    return False

@app.route('/')
def home():
    """Trang chủ"""
    return jsonify({
        "service": "ICExAI Auth Server",
        "status": "online",
        "version": "2.0",
        "endpoints": {
            "verify": "/verify (POST)",
            "admin": "/admin (GET)",
            "health": "/health (GET)"
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "ok", "time": int(time.time())})

@app.route('/verify', methods=['POST'])
def verify():
    """API verify key"""
    try:
        data = request.json
        key = data.get('key', '').strip()
        hwid = data.get('hwid', '').strip()
        
        if not key or not hwid:
            return jsonify({"success": False, "message": "Missing key or HWID"}), 400
        
        hwid_hash = get_hwid_hash(hwid)
        keys = load_keys()
        
        for k in keys:
            if k.get('key') == key:
                # Check expiry
                if check_expiry(k):
                    k['status'] = 'expired'
                    save_keys(keys)
                    return jsonify({"success": False, "message": "Key expired"}), 403
                
                # Check HWID
                current_hwid = k.get('hwid', '')
                
                if not current_hwid or current_hwid == 'Waiting...':
                    # First activation
                    k['hwid'] = hwid_hash
                    k['status'] = 'active'
                    save_keys(keys)
                    print(f"[ACTIVATED] {key} | {k.get('owner', 'Unknown')}")
                    return jsonify({
                        "success": True,
                        "message": "Activated successfully",
                        "owner": k.get('owner', 'User'),
                        "total_hours": k.get('total', 24)
                    })
                elif current_hwid == hwid_hash:
                    # HWID match
                    print(f"[VERIFIED] {key} | {k.get('owner', 'Unknown')}")
                    return jsonify({
                        "success": True,
                        "message": "Verified",
                        "owner": k.get('owner', 'User'),
                        "total_hours": k.get('total', 24)
                    })
                else:
                    # HWID mismatch
                    return jsonify({"success": False, "message": "Key locked to another device"}), 403
        
        return jsonify({"success": False, "message": "Invalid key"}), 403
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"success": False, "message": "Server error"}), 500

@app.route('/admin')
def admin():
    """Admin panel - Xem danh sách key"""
    keys = load_keys()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ICExAI Admin Panel</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; margin: 20px; background: #1a1a1a; color: #fff; }
            h1 { color: #4CAF50; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
            th { background: #2d2d2d; color: #4CAF50; }
            tr:hover { background: #2d2d2d; }
            .active { color: #4CAF50; }
            .expired { color: #f44336; }
            .inactive { color: #ff9800; }
        </style>
    </head>
    <body>
        <h1>🔐 ICExAI Admin Panel</h1>
        <p>Total Keys: <strong>{{ total }}</strong></p>
        <table>
            <tr>
                <th>Key</th>
                <th>Owner</th>
                <th>Status</th>
                <th>HWID</th>
                <th>Total Hours</th>
                <th>Expire At</th>
            </tr>
            {% for key in keys %}
            <tr>
                <td><code>{{ key.key }}</code></td>
                <td>{{ key.owner }}</td>
                <td class="{{ key.status }}">{{ key.status }}</td>
                <td>{{ key.hwid[:8] if key.hwid else 'Not activated' }}</td>
                <td>{{ key.total }}h</td>
                <td>{{ key.expire_at if key.expire_at else 'N/A' }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(html)
    return template.render(keys=keys, total=len(keys))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("="*60)
    print("  ICExAI Auth Server")
    print("="*60)
    print(f"  Port: {port}")
    print(f"  Keys: {KEYS_FILE}")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
