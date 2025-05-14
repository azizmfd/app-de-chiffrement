from flask import Flask, request, send_file, jsonify, render_template, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from encryption import aes_gcm_encrypt, aes_gcm_decrypt
from intelligence import analyse_contenu_sensible

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECURITY_FILE = "security_log.json"
ADMIN_PASSWORD = "admin123"

def load_security():
    if os.path.exists(SECURITY_FILE):
        try:
            with open(SECURITY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_security(data):
    with open(SECURITY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_blocked(ip):
    data = load_security()
    info = data.get(ip)
    if not info:
        return False, 0

    now = datetime.now()
    level = info.get("level", 0)
    last_fail = datetime.fromisoformat(info["last_fail"])

    delays = [0, 60, 300, 3600]
    if level >= len(delays):
        return True, -1

    elapsed = (now - last_fail).total_seconds()
    if elapsed < delays[level]:
        return True, delays[level] - elapsed

    return False, 0

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files or 'key' not in request.form:
        return jsonify({'error': 'Fichier ou clé manquant'}), 400

    file = request.files['file']
    key = request.form['key'].encode()
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, f"{filename}.enc")
    file.save(input_path)

    aes_gcm_encrypt(input_path, output_path, key)
    return send_file(output_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files or 'key' not in request.form:
        return jsonify({'error': 'Fichier ou clé manquant'}), 400

    ip = request.remote_addr
    blocked, remaining = is_blocked(ip)
    if blocked:
        if remaining == -1:
            return jsonify({'error': "⛔ Accès bloqué. Contacter l'administrateur."}), 403
        return jsonify({'error': f"⏱ Accès temporairement bloqué ({int(remaining)} sec)"}), 403

    file = request.files['file']
    key = request.form['key'].encode()
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, f"{filename}.dec")
    file.save(input_path)

    try:
        aes_gcm_decrypt(input_path, output_path, key)
        data = load_security()
        if ip in data:
            del data[ip]
            save_security(data)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        data = load_security()
        fail = data.get(ip, {"level": 0})
        fail["level"] = min(fail.get("level", 0) + 1, 4)
        fail["last_fail"] = datetime.now().isoformat()
        data[ip] = fail
        save_security(data)
        return jsonify({'error': str(e)}), 400

@app.route('/analyse_ai', methods=['POST'])
def analyse_ai():
    if 'file' not in request.files:
        return jsonify({'error': 'Fichier manquant'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    result, message = analyse_contenu_sensible(input_path)
    return jsonify({"sensibles": bool(result), "message": message})

@app.route('/admin')
def admin_page():
    password = request.args.get("pass")
    if password != ADMIN_PASSWORD:
        return "🔒 Accès refusé. Ajoute ?pass=admin123 dans l'URL pour accéder."
    data = load_security()
    return render_template("admin_interface.html", ip_data=data)

@app.route('/admin/unblock/<ip>')
def admin_unblock(ip):
    password = request.args.get("pass")
    if password != ADMIN_PASSWORD:
        return "🔒 Accès refusé."
    data = load_security()
    if ip in data:
        del data[ip]
        save_security(data)
        return redirect(f"/admin?pass={ADMIN_PASSWORD}")
    return f"ℹ️ IP {ip} non trouvée."

if __name__ == '__main__':
    app.run(debug=True)
