from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

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
# Disease Mapping
# ===============================
DISEASE_MAP = {
    0: 'Anemia', 1: 'Polycythemia', 2: 'Leukocytosis',
    3: 'Leukopenia', 4: 'Thrombocytopenia',
    5: 'Thrombocytosis', 6: 'Neutropenia',
    7: 'Neutrophilia', 8: 'Lymphocytopenia',
    9: 'Lymphocytosis', 10: 'Monocytes High',
    11: 'Eosinophil High', 12: 'Basophil High',
    13: 'Normal'
}

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
# Train Model ONCE
# ===============================
def train_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_dir, "Training.csv"))

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

@app.route("/")
def home():
    return "Flask app deployed successfully!"

# ===============================
# Register
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form["password"] != request.form["confirm_password"]:
            return render_template("register.html", error="Passwords do not match")

        if users_collection.find_one({"username": request.form["username"]}):
            return render_template("register.html", error="Username already exists")

        users_collection.insert_one({
            "username": request.form["username"],
            "email": request.form["email"],
            "password": generate_password_hash(request.form["password"]),
            "age": int(request.form["age"]),
            "gender": request.form["gender"],
            "created_at": datetime.utcnow()
        })

        return redirect(url_for("login", success="Registration successful!"))

    return render_template("register.html")

# ===============================
# Login
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")

    if request.method == "POST":
        user = users_collection.find_one({"username": request.form["username"]})

        if user and check_password_hash(user["password"], request.form["password"]):
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
        values = [float(request.form[k]) for k in
                  ["WBC", "RBC", "HGB", "PLT", "NEUT", "LYMPH", "MONO", "EO", "BASO"]]

        prediction = int(model.predict([values])[0])

        history_collection.insert_one({
            "user_id": session["user_id"],
            "username": session["username"],
            "WBC": values[0],
            "RBC": values[1],
            "HGB": values[2],
            "PLT": values[3],
            "NEUT": values[4],
            "LYMPH": values[5],
            "MONO": values[6],
            "EO": values[7],
            "BASO": values[8],
            "disease_code": prediction,
            "disease_name": DISEASE_MAP[prediction],
            "created_at": datetime.utcnow()
        })

        return render_template(
            "result.html",
            disease=DISEASE_MAP[prediction],
            cause=DISEASE_CAUSES[prediction]
        )

    return render_template("afterlogin.html", username=session["username"])

# ===============================
# View History
# ===============================
@app.route("/view_history")
def view_history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    history = list(
        history_collection.find(
            {"user_id": session["user_id"]}
        ).sort("created_at", -1)
    )

    for record in history:
        record["id"] = str(record["_id"])   # ✅ FIX
        record["created_at"] = record["created_at"].strftime("%Y-%m-%d %H:%M")

    return render_template("history.html", history=history)



# ===============================
# Delete History
# ===============================
@app.route("/delete_history/<record_id>")
def delete_history(record_id):
    history_collection.delete_one({
        "_id": ObjectId(record_id),
        "user_id": session["user_id"]
    })
    return redirect(url_for("view_history"))

# ===============================
# Download History
# ===============================
@app.route("/download_history")
def download_history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    history = list(
        history_collection.find(
            {"user_id": session["user_id"]}
        ).sort("created_at", -1)
    )

    if not history:
        return redirect(url_for("view_history"))

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    table_data = [
        ["Date", "WBC", "RBC", "HGB", "PLT", "Disease"]
    ]

    for r in history:
        table_data.append([
            r["created_at"].strftime("%Y-%m-%d %H:%M"),
            r["WBC"],
            r["RBC"],
            r["HGB"],
            r["PLT"],
            r["disease_name"]
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    pdf.build([table])
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="blood_test_history.pdf",
        mimetype="application/pdf"
    )


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
