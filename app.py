from flask import Flask, request, Response
import requests
import os

# =========================================================
# TETAPAN KASTAM DNS (Integrasi Purple DNS: 94.140.14.14)
# Digunakan oleh server ini untuk cari jalan ke 1Fichier
# =========================================================
try:
    import dns.resolver
    import urllib3.util.connection
    
    original_create_connection = urllib3.util.connection.create_connection

    def custom_create_connection(address, *args, **kwargs):
        host, port = address
        try:
            if host.replace('.', '').isdigit():
                ip = host
            else:
                resolver = dns.resolver.Resolver(configure=False)
                resolver.nameservers = ['94.140.14.14', '94.140.15.15']
                answers = resolver.resolve(host, 'A')
                ip = answers[0].to_text()
        except Exception:
            ip = host

        return original_create_connection((ip, port), *args, **kwargs)

    urllib3.util.connection.create_connection = custom_create_connection
    print("✅ Enjin Purple DNS berjaya diaktifkan di server!")
except ImportError:
    print("⚠️ Module 'dnspython' tidak dijumpai.")
# =========================================================

app = Flask(__name__)

# Kunci diambil dari persekitaran rahsia
API_KEY = os.environ.get("API_KEY_1FICHIER")

@app.route('/play')
def play_video():
    file_id = request.args.get('id')
    
    if not file_id:
        return "RALAT: Sila masukkan ID fail.", 400

    url_fail = f"https://1fichier.com/?{file_id}"
    url_api = "https://api.1fichier.com/v1/download/get_token.cgi"
    
    headers_api = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": url_fail, "inline": 1}
    
    try:
        # 1. Dapatkan Link Sebenar dari 1Fichier
        respons = requests.post(url_api, json=payload, headers=headers_api)
        if respons.status_code != 200:
            return f"Ralat 1Fichier: {respons.status_code}", 500
            
        pautan_terus = respons.json().get("url")
        if not pautan_terus:
            return f"Gagal menjana pautan.", 500

        # =========================================================
        # 2. TEKNIK PROXY (ORANG TENGAH)
        # Daripada buat "Redirect", kita sedut video dan pass kepada user
        # =========================================================
        
        # Ambil header 'Range' dari Player TV (penting untuk skip/forward video)
        req_headers = {}
        if 'Range' in request.headers:
            req_headers['Range'] = request.headers['Range']
            
        # Minta video dari 1Fichier secara "Streaming" (sedut sikit-sikit)
        r = requests.get(pautan_terus, headers=req_headers, stream=True)
        
        # Fungsi untuk pam (pump) data video ke Player pengguna
        def generate_video_stream():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        # Hantar response kepada pengguna berserta header asal video
        proxy_response = Response(generate_video_stream(), status=r.status_code)
        
        # Salin header penting dari 1Fichier (seperti saiz file, jenis file)
        for key, value in r.headers.items():
            if key.lower() not in ['transfer-encoding', 'content-encoding', 'connection']:
                proxy_response.headers[key] = value
                
        return proxy_response

    except Exception as e:
        return f"Ralat Sistem: {str(e)}", 500
