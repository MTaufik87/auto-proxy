from flask import Flask, request, redirect
import requests
import os

# =========================================================
# TETAPAN KASTAM DNS (Integrasi Purple DNS: 94.140.14.14)
# =========================================================
try:
    import dns.resolver
    import urllib3.util.connection
    
    original_create_connection = urllib3.util.connection.create_connection

    def custom_create_connection(address, *args, **kwargs):
        host, port = address
        try:
            # Semak jika ia sudah IP address
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
    print("✅ Enjin Purple DNS berjaya diaktifkan!")
except ImportError:
    print("⚠️ Module 'dnspython' tidak dijumpai. Sila pastikan ia ada dalam requirements.txt")
# =========================================================

app = Flask(__name__)

# Kunci diambil dari persekitaran rahsia Vercel
API_KEY = os.environ.get("API_KEY_1FICHIER")

@app.route('/play')
def play_video():
    file_id = request.args.get('id')
    
    if not file_id:
        return "RALAT: Sila masukkan ID fail.", 400

    url_fail = f"https://1fichier.com/?{file_id}"
    
    # URL ini telah dibersihkan daripada kurungan pelik
    url_api = "https://api.1fichier.com/v1/download/get_token.cgi"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": url_fail, "inline": 1}
    
    try:
        respons = requests.post(url_api, json=payload, headers=headers)
        if respons.status_code == 200:
            pautan_terus = respons.json().get("url")
            if pautan_terus:
                return redirect(pautan_terus)
            return f"Gagal menjana pautan: {respons.json()}", 500
        return f"Ralat 1Fichier: {respons.status_code}", 500
    except Exception as e:
        return f"Ralat Sistem: {str(e)}", 500
