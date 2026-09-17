from flask import Flask, request, send_file, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from encryption import aes_gcm_encrypt, aes_gcm_decrypt
from intelligence import analyse_contenu_sensible
from flask import send_from_directory

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECURITY_FILE = "security_log.json"
ADMIN_PASSWORD = "admin123"

# Clé secrète nécessaire pour les sessions
app.secret_key = os.urandom(24)

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
        return jsonify({'error': 'File or key missing'}), 400

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
        return jsonify({'error': 'File or key missing'}), 400

    ip = request.remote_addr
    blocked, remaining = is_blocked(ip)
    if blocked:
        if remaining == -1:
            return jsonify({'error': "⛔ Access blocked. Contact the administrator."}), 403
        return jsonify({'error': f"⏱ Temporary access blocked ({int(remaining)} sec)"}), 403

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
        return jsonify({'error': 'File missing'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    result, message = analyse_contenu_sensible(input_path)
    return jsonify({"sensibles": bool(result), "message": message})

# Nouvelle route login (GET pour formulaire, POST pour validation)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_page'))
        else:
            return render_template('login.html', error="Incorrect password.")
    return render_template('login.html')

# Page admin protégée par session
@app.route('/admin')
def admin_page():
    if not session.get('admin'):
        return redirect(url_for('login'))
    data = load_security()
    return render_template("admin_interface.html", ip_data=data)

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# Débloquer IP, protégé aussi par session
@app.route('/admin/unblock/<ip>')
def admin_unblock(ip):
    if not session.get('admin'):
        return redirect(url_for('login'))
    data = load_security()
    if ip in data:
        del data[ip]
        save_security(data)
        return redirect(url_for('admin_page'))
    return f"ℹ️ IP {ip} not found."

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend_files(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
