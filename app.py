import os
import mimetypes
from flask import Flask, send_from_directory

# Ensure the browser knows how to handle WASM files
mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('application/octet-stream', '.so')

app = Flask(__name__, static_folder='build/web', static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # This is the critical fix: it looks for the file in your build/web folder
    # even if the path has many subdirectories.
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
