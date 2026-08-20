from flask import Flask, render_template, request, send_from_directory, redirect
from werkzeug.utils import secure_filename
import os
import sqlite3
import uuid
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
def init_db():

    conn = sqlite3.connect("surprises.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS surprises (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            occasion TEXT NOT NULL,
            message TEXT NOT NULL,
            photo TEXT
        )
    """)

    conn.commit()
    conn.close()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("home.html")
    
    
@app.route("/surprise", methods=["POST"])
def surprise():

    name = request.form["name"]
    occasion = request.form["occasion"]
    message = request.form["message"]

    photo = request.files.get("photo")

    filename = None

    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    surprise_id = str(uuid.uuid4())[:8]

    conn = sqlite3.connect("surprises.db")

    conn.execute("""
        INSERT INTO surprises
        (id, name, occasion, message, photo)
        VALUES (?, ?, ?, ?, ?)
    """, (
        surprise_id,
        name,
        occasion,
        message,
        filename
    ))

    conn.commit()
    conn.close()

    return redirect("/s/" + surprise_id)
  
@app.route("/s/<surprise_id>")
def show_surprise(surprise_id):

    conn = sqlite3.connect("surprises.db")
    conn.row_factory = sqlite3.Row

    surprise = conn.execute(
        "SELECT * FROM surprises WHERE id = ?",
        (surprise_id,)
    ).fetchone()

    conn.close()

    if surprise is None:
        return "Surprise not found", 404

    return render_template(
        "surprise.html",
        name=surprise["name"],
        occasion=surprise["occasion"],
        message=surprise["message"],
        photo=surprise["photo"],
        surprise_id=surprise_id
    )



if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )