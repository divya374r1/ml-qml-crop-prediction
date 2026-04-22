from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import os
from werkzeug.utils import secure_filename

from utils.languages import LANGUAGES
from utils.weather import get_weather
from utils.ml_model import CropYieldML
from utils.qml_model import CropYieldQML
from utils.feature_engineering import build_feature_vector
from utils.crop_rules import check_crop_suitability
from utils.llm_explainer import explain_prediction   # ✅ NEW

app = Flask(__name__)
app.secret_key = "qml_crop_secret_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- DB ----------------
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


# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------- LOGIN ----------------
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


# ---------------- LANGUAGE ----------------
@app.route("/language", methods=["GET", "POST"])
def language():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        session["language"] = request.form["language"]
        return redirect(url_for("dashboard"))

    return render_template("language.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    language = session.get("language", "en")
    texts = LANGUAGES.get(language, LANGUAGES["en"])

    return render_template("dashboard.html", texts=texts, language=language)


# ---------------- HELPER ----------------
def suggest_best_crops(state, temperature, rainfall):
    crops = ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Tea", "Coffee"]
    results = []
    ml = CropYieldML()

    for crop in crops:
        status, _ = check_crop_suitability(crop, temperature, rainfall)

        if status != "Not Suitable":
            X = build_feature_vector({
                "temperature": temperature,
                "rainfall": rainfall,
                "crop": crop,
                "state": state
            })
            pred = ml.predict(X)
            results.append((crop, pred))

    results.sort(key=lambda x: x[1], reverse=True)
    return [c[0] for c in results[:3]]


# =====================================================
# LOCATION INPUT
# =====================================================
@app.route("/input/location", methods=["GET", "POST"])
def input_location():
    if "user" not in session:
        return redirect(url_for("login"))

    language = session.get("language", "en")
    texts = LANGUAGES.get(language, LANGUAGES["en"])

    if request.method == "POST":
        state = request.form["state"]
        district = request.form["district"]
        crop = request.form["crop"]
        acre = float(request.form.get("acre", 1))

        temperature, rainfall = get_weather(district, state)

        if rainfall == 0:
            rainfall = 120

        suitability, reason = check_crop_suitability(crop, temperature, rainfall)

        X = build_feature_vector({
            "temperature": temperature,
            "rainfall": rainfall,
            "crop": crop,
            "state": state
        })

        ml = CropYieldML()
        qml = CropYieldQML()

        ml_total = ml.predict(X) * acre
        qml_total = qml.predict(X) * acre

        top_crops = suggest_best_crops(state, temperature, rainfall)

        # ✅ CLEAN ADVICE
        if suitability == "Suitable":
            advice = "Good conditions. You can proceed."
        elif suitability == "Moderately Suitable":
            advice = "Use irrigation and proper care."
        else:
            advice = "Not recommended for this region."

        # ✅ FINAL EXPLANATION (LLM)
        explanation = explain_prediction(
            crop,
            temperature,
            rainfall,
            ml_total,
            qml_total,
            suitability,
            advice,
            top_crops,
            language
        )

        return render_template(
            "result.html",
            explanation=explanation,
            ml_yield=ml_total,
            qml_yield=qml_total
        )

    return render_template("input_location.html", texts=texts)


# =====================================================
# MANUAL INPUT
# =====================================================
@app.route("/input/manual", methods=["GET", "POST"])
def input_manual():
    if "user" not in session:
        return redirect(url_for("login"))

    language = session.get("language", "en")
    texts = LANGUAGES.get(language, LANGUAGES["en"])

    if request.method == "POST":
        crop = request.form["crop"]
        acre = float(request.form.get("acre", 1))

        temp_map = {"low": 20, "medium": 28, "high": 35}
        rain_map = {"low": 50, "medium": 120, "high": 250}

        temperature = temp_map[request.form["temperature"]]
        rainfall = rain_map[request.form["rainfall"]]

        X = build_feature_vector({
            "temperature": temperature,
            "rainfall": rainfall,
            "crop": crop,
            "state": "Other"
        })

        ml = CropYieldML()
        qml = CropYieldQML()

        ml_total = ml.predict(X) * acre
        qml_total = qml.predict(X) * acre

        explanation = explain_prediction(
            crop,
            temperature,
            rainfall,
            ml_total,
            qml_total,
            "Moderate",
            "Maintain soil and irrigation.",
            [],
            language
        )

        return render_template(
            "result.html",
            explanation=explanation,
            ml_yield=ml_total,
            qml_yield=qml_total
        )

    return render_template("input_manual.html", texts=texts)


# =====================================================
# IMAGE INPUT
# =====================================================
@app.route("/input/image", methods=["GET", "POST"])
def input_image():
    if "user" not in session:
        return redirect(url_for("login"))

    language = session.get("language", "en")
    texts = LANGUAGES.get(language, LANGUAGES["en"])

    if request.method == "POST":
        image = request.files["image"]
        acre = float(request.form.get("acre", 1))

        filename = secure_filename(image.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(path)

        # Dummy logic
        crop = "Rice"
        temperature, rainfall = 28, 120

        X = build_feature_vector({
            "temperature": temperature,
            "rainfall": rainfall,
            "crop": crop,
            "state": "Other"
        })

        ml = CropYieldML()
        qml = CropYieldQML()

        ml_total = ml.predict(X) * acre
        qml_total = qml.predict(X) * acre

        explanation = explain_prediction(
            crop,
            temperature,
            rainfall,
            ml_total,
            qml_total,
            "Unknown",
            "Image model not implemented yet.",
            [],
            language
        )

        return render_template(
            "result.html",
            explanation=explanation,
            ml_yield=ml_total,
            qml_yield=qml_total
        )

    return render_template("input_image.html", texts=texts)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)