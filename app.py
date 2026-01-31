import os
from flask import Flask, send_from_directory

# We point static_folder to the exact subfolder pygbag creates
app = Flask(__name__, static_folder='build/web')

@app.route('/')
def index():
    # This serves the main game page
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # This serves the .wasm, .js, and .data files
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
