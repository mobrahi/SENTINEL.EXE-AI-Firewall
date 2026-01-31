import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='build/web', static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    response = send_from_directory(app.static_folder, path)
    # Force the browser to treat .so and .wasm as binary data
    if path.endswith('.wasm'):
        response.headers['Content-Type'] = 'application/wasm'
    if path.endswith('.so'):
        response.headers['Content-Type'] = 'application/octet-stream'
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
