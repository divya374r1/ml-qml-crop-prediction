from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import os
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename

# ---------- IMPORTS ----------
from utils.languages import LANGUAGES
from utils.weather import get_weather
from utils.ml_model import CropYieldML
from utils.qml_model import CropYieldQML
from utils.llm_explainer import explain_prediction

# ---------- APP SETUP ----------
app = Flask(__name__)
app.secret_key = "qml_crop_secret_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("users.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------- AUTH ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (request.form["username"], request.form["password"])
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            conn.close()
            return "Username already exists"
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = request.form["username"]
            return redirect(url_for("language"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/language", methods=["GET", "POST"])
def language():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        session["language"] = request.form["language"]
        return redirect(url_for("dashboard"))
    return render_template("language.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    language = session.get("language","en")
    texts = LANGUAGES.get(language, LANGUAGES["en"])

    return render_template(
        "dashboard.html",
        texts=texts,
        language=language
    )
# =====================================================
# 1️⃣ LOCATION INPUT
# =====================================================
@app.route("/input/location", methods=["GET", "POST"])
def input_location():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        state = request.form["state"]
        district = request.form["district"]
        crop = request.form["crop"]

        temperature, rainfall = get_weather(district, state)

        X = [[temperature / 50, rainfall / 500, 0.5, 0.3]]

        ml = CropYieldML()
        ml.train(X, [3.0])
        ml_pred = float(ml.predict(X))

        qml = CropYieldQML()
        qml_pred = float(qml.predict(X))

        session["result_data"] = {
            "explanation": explain_prediction(
                crop, temperature, rainfall, ml_pred, qml_pred,
                session.get("language", "en")
            ),
            "ml_yield": ml_pred,
            "qml_yield": qml_pred
        }

        return redirect(url_for("result"))

    texts = LANGUAGES.get(session.get("language", "en"))
    return render_template("input_location.html", texts=texts)

# =====================================================
# 2️⃣ MANUAL INPUT
# =====================================================
@app.route("/input/manual", methods=["GET", "POST"])
def input_manual():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        crop = request.form["crop"]

        temp_map = {"low": 20, "medium": 30, "high": 40}
        rain_map = {"low": 50, "medium": 150, "high": 300}
        soil_map = {"sandy": 0.3, "clay": 0.6, "loamy": 0.8}

        temperature = temp_map[request.form["temperature"]]
        rainfall = rain_map[request.form["rainfall"]]
        soil = soil_map[request.form["soil"]]

        X = [[temperature / 50, rainfall / 500, soil, 0.3]]

        ml = CropYieldML()
        ml.train(X, [2.8])
        ml_pred = float(ml.predict(X))

        qml = CropYieldQML()
        qml_pred = float(qml.predict(X))

        session["result_data"] = {
            "explanation": explain_prediction(
                crop, temperature, rainfall, ml_pred, qml_pred,
                session.get("language", "en")
            ),
            "ml_yield": ml_pred,
            "qml_yield": qml_pred
        }

        return redirect(url_for("result"))

    return render_template("input_manual.html")

# ====================================================
# 3️⃣ IMAGE INPUT
# =====================================================
@app.route("/input/image", methods=["GET", "POST"])
def input_image():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        # ---- CHECK FILE ----
        if "image" not in request.files:
            return "No image file provided"

        image = request.files["image"]

        if image.filename == "":
            return "No image selected"

        crop = request.form.get("crop", "Unknown")

        # ---- SAVE IMAGE ----
        filename = secure_filename(image.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        try:
            image.save(path)
        except:
            return "Image upload failed"

        # ---- IMAGE PROCESSING ----
        try:
            img = Image.open(path).convert("L")
            arr = np.array(img)

            brightness = np.mean(arr) / 255
            size_feature = arr.size / 1000000

        except:
            return "Invalid image file"

        # ---- ASSUMED ENVIRONMENT ----
        temperature = 28
        rainfall = 120

        # ---- FEATURE VECTOR ----
        X = [[brightness, size_feature, 0.5, 0.3]]

        # ---- ML MODEL ----
        ml = CropYieldML()
        ml.train(X, [3.1])
        ml_pred = float(ml.predict(X))

        # ---- QML MODEL ----
        qml = CropYieldQML()
        qml_pred = float(qml.predict(X))

        # ---- EXPLANATION ----
        explanation = explain_prediction(
            crop,
            temperature,
            rainfall,
            ml_pred,
            qml_pred,
            session.get("language", "en")
        )

        # ---- SAVE RESULT ----
        session["result_data"] = {
            "explanation": explanation,
            "ml_yield": ml_pred,
            "qml_yield": qml_pred
        }

        return redirect(url_for("result"))

    return render_template("input_image.html")

# ---------- RESULT ----------
@app.route("/result")
def result():
    if "user" not in session:
        return redirect(url_for("login"))

    data = session.get("result_data")
    if not data:
        return redirect(url_for("dashboard"))

    return render_template(
        "result.html",
        explanation=data["explanation"],
        ml_yield=data["ml_yield"],
        qml_yield=data["qml_yield"]
    )

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
