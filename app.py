import os
import mimetypes
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='build/web', static_url_path='')

# Add ALL types needed for Pygame-Web
mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('application/octet-stream', '.so')
mimetypes.add_type('application/octet-stream', '.apk')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/plain', '.py')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # This handles requests for pythonrc.py or any other asset
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
