"""
Gidrometeorologiya xizmati — Ob-havo prognozi xarita generatori
Soddalashtirilgan server: faqat statik fayllar + HTML sahifa
"""
import os
from pathlib import Path
from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
