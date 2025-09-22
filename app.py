#library
from flask import Flask, request, render_template, jsonify
from Crypto.Cipher import AES
import base64
import hashlib

app = Flask(__name__)

#kunci AES 32 byte seterah kita
SECRET_KEY = hashlib.sha256(b"yangbikintampansekali").digest()

#Data dummy untuk demo
users = {
    "12345": {"name": "zaky", "jabatan": "CEO"},
    "67890": {"name": "fadil", "jabatan": "Manager"},
}

#fungsi enkripsi
def encrypt(text):
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode())
    return base64.urlsafe_b64encode(cipher.nonce + ciphertext).decode()

#fungsi dekripsi
def decrypt(encrypted_text):
    raw = base64.urlsafe_b64decode(encrypted_text)
    nonce = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted = cipher.decrypt(ciphertext)
    return decrypted.decode()

#halaman utama
@app.route("/")
def home():
    return render_template("index.html")

#API untuk enkripsi ID → UID
@app.route("/encrypt")
def encrypt_route():
    user_id = request.args.get("id", "")
    if not user_id:
        return "?id=....", 400
    uid = encrypt(user_id)
    return jsonify({
        #asli
        "1_original_id":user_id,
        "1_original_url":f"http://localhost:5000/profile_plain?id={user_id}",
        #enkrip
        "2_encrypted_uid":uid,
        "2_encrypted_url":f"http://localhost:5000/profile?uid={uid}"
    })

#API
#membuka profil url id asli   
@app.route("/profile_plain")
def profile_plain():
    user_id = request.args.get("id", "")
    if not user_id:
        return "Hasil ?id=asli", 400
    if user_id in users:
        data = users[user_id]
        return f"""
        <h1>Profil User (polos)</h1>
        <p><b>ID:</b> {user_id}</p>
        <p><b>Nama:</b> {data['name']}</p>
        <p><b>jabatan:</b> {data['jabatan']}</p>
        """
    else:
        return f"User dengan ID {user_id} tidak ada!"

#membuka profil url uid terenkripsi
@app.route("/profile")
def profile_route():
    uid = request.args.get("uid", "")
    if not uid:
        return "Hasil ?uid=enkrip", 400
    try:
        user_id = decrypt(uid)
        if user_id in users:
            data = users[user_id]
            return f"""
            <h1>Profil User (enkrip)</h1>
            <p><b>ID:</b> {user_id}</p>
            <p><b>Nama:</b> {data['name']}</p>
            <p><b>jabatan:</b> {data['jabatan']}</p>
            """
        else:
            return f"User dengan ID {user_id} tidak ada!"
    except:
        return "UID tidak valid!", 400

if __name__ == "__main__":
    app.run(debug=True)