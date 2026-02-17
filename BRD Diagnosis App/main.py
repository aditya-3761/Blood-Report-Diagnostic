from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_CHANGE_THIS"

# ===============================
# MongoDB Connection
# ===============================
client = MongoClient("mongodb://localhost:27017/")
db = client["blood_diagnostic_db"]

users_collection = db["users"]
history_collection = db["user_history"]


# ===============================
# Disease Name Mapping
# ===============================
DISEASE_MAP = {
    0: 'Anemia',
    1: 'Polycythemia',
    2: 'Leukocytosis',
    3: 'Leukopenia',
    4: 'Thrombocytopenia',
    5: 'Thrombocytosis',
    6: 'Neutropenia',
    7: 'Neutrophilia',
    8: 'Lymphocytopenia',
    9: 'Lymphocytosis',
    10: 'Monocytes High',
    11: 'Eosinophil High',
    12: 'Basophil High',
    13: 'Normal'
}

# ===============================
# Disease Causes
# ===============================
DISEASE_CAUSES = {
    0: "Anemia is caused by low hemoglobin or RBC.",
    1: "Polycythemia is caused by high RBC count.",
    2: "Leukocytosis indicates infection or inflammation.",
    3: "Leukopenia indicates low immunity.",
    4: "Thrombocytopenia causes bleeding risk.",
    5: "Thrombocytosis increases clot risk.",
    6: "Neutropenia increases infection risk.",
    7: "Neutrophilia indicates bacterial infection.",
    8: "Lymphocytopenia weakens immunity.",
    9: "Lymphocytosis often due to viral infection.",
    10: "High monocytes indicate chronic infection.",
    11: "High eosinophils indicate allergy.",
    12: "High basophils indicate inflammation.",
    13: "Blood values are normal."
}


# ===============================
# Train Model
# ===============================
def train_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(BASE_DIR, "Training.csv"))

    X = df.drop("Disease", axis=1)
    y = df["Disease"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

model = train_model()
# ===============================
# Load & Train Model (ONCE)
# ===============================
def train_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(BASE_DIR, "Training.csv"))

    X = df.drop("Disease", axis=1)
    y = df["Disease"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

model = train_model()

# ===============================
# Routes
# ===============================
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("afterlogin"))
    return redirect(url_for("login"))

# ===============================
# Register
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        age = request.form["age"]
        gender = request.form["gender"]

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        if users_collection.find_one({"username": username}):
            return render_template("register.html", error="Username already exists")

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "age": int(age),
            "gender": gender,
            "created_at": datetime.utcnow()
        })

        return redirect(url_for("login", success="Registration successful!"))

    return render_template("register.html")

# ===============================
# guest
# ===============================

@app.route("/guest", methods=["GET", "POST"])
def guest():
    if request.method == "POST":
        try:
            values = [
                float(request.form["WBC"]),
                float(request.form["RBC"]),
                float(request.form["HGB"]),
                float(request.form["PLT"]),
                float(request.form["NEUT"]),
                float(request.form["LYMPH"]),
                float(request.form["MONO"]),
                float(request.form["EO"]),
                float(request.form["BASO"])
            ]

            prediction = int(model.predict([values])[0])
            disease_name = DISEASE_MAP.get(prediction, "Unknown")

            return render_template(
                "result.html",
                disease=disease_name,
                cause="Login required to save history"
            )

        except Exception as e:
            return render_template("result.html", disease="Error", cause=str(e))

    return render_template("afterlogin.html", username="Guest")


# ===============================
# Login
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            return redirect(url_for("afterlogin"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html", success=success)

# ===============================
# After Login
# ===============================
@app.route("/afterlogin", methods=["GET", "POST"])
def afterlogin():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            values = [
                float(request.form.get("WBC")),
                float(request.form.get("RBC")),
                float(request.form.get("HGB")),
                float(request.form.get("PLT")),
                float(request.form.get("NEUT")),
                float(request.form.get("LYMPH")),
                float(request.form.get("MONO")),
                float(request.form.get("EO")),
                float(request.form.get("BASO"))
            ]

            if model is None:
                return render_template(
                    "result.html",
                    disease="Model Error",
                    cause="ML model not loaded"
                )

            prediction = int(model.predict([values])[0])
            disease_name = DISEASE_MAP[prediction]
            disease_cause = DISEASE_CAUSES[prediction]

            return render_template(
                "result.html",
                disease=disease_name,
                cause=disease_cause
            )

        except Exception as e:
            return render_template(
                "result.html",
                disease="Error",
                cause=str(e)
            )

    return render_template("afterlogin.html", username=session["username"])



# ===============================
# View History
# ===============================
@app.route("/view_history")
def view_history():
    history = list(history_collection.find(
        {"user_id": session["user_id"]}
    ).sort("created_at", -1))

    for r in history:
        r["id"] = str(r["_id"])

    return render_template("history.html", history=history)

# ===============================
# Delete History
# ===============================
@app.route("/delete_history/<record_id>")
def delete_history(record_id):
    history_collection.delete_one({"_id": ObjectId(record_id)})
    return redirect(url_for("view_history"))

# ===============================
# Logout
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ===============================
if __name__ == "__main__":
    app.run(debug=True)
