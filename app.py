from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

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
        # Dapatkan pautan terus daripada 1Fichier melalui pelayan Render
        respons = requests.post(url_api, json=payload, headers=headers, timeout=15)
        if respons.status_code != 200:
            return f"Ralat 1Fichier: {respons.status_code}", 500
            
        pautan_terus = respons.json().get("url")
        if not pautan_terus:
            return "Gagal mendapatkan pautan video.", 500

        # Alirkan (Stream) video melalui pelayan Render ke peranti pengguna
        req_video = requests.get(pautan_terus, stream=True, timeout=20)
        
        return Response(
            req_video.iter_content(chunk_size=1024*64),
            status=req_video.status_code,
            content_type=req_video.headers.get('content-type', 'video/mp4'),
            direct_passthrough=True
        )
        
    except Exception as e:
        return f"Ralat Sistem: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
