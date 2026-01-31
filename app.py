import os
import mimetypes
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='build/web')

# Explicitly set MIME types for WASM and Pygame assets
mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('application/octet-stream', '.so')
mimetypes.add_type('application/octet-stream', '.apk')
mimetypes.add_type('text/javascript', '.js')

@app.after_request
def add_header(response):
    # These headers are required for some WASM environments
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
