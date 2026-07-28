from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

# Kunci API 1Fichier daripada persekitaran Vercel
API_KEY = os.environ.get("API_KEY_1FICHIER")

@app.route('/play')
def play_video():
    file_id = request.args.get('id')
    
    if not file_id:
        return "RALAT: Sila masukkan ID fail.", 400

    url_fail = f"https://1fichier.com/?{file_id}"
    url_api = "https://api.1fichier.com/v1/download/get_token.cgi"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": url_fail, "inline": 1}
    
    try:
        # Menghantar permintaan kepada 1Fichier dengan masa menunggu (timeout) 10 saat
        respons = requests.post(url_api, json=payload, headers=headers, timeout=10)
        if respons.status_code == 200:
            pautan_terus = respons.json().get("url")
            if pautan_terus:
                # Menghalakan pemain OTT terus ke pautan video
                return redirect(pautan_terus)
            return f"Gagal menjana pautan: {respons.json()}", 500
        return f"Ralat 1Fichier: {respons.status_code}", 500
    except requests.exceptions.Timeout:
        return "Ralat: Pelayan 1Fichier lewat memberi respons.", 500
    except Exception as e:
        return f"Ralat Sistem: {str(e)}", 500
