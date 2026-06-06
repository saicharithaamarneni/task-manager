from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)
import os

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import db, User, Task

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "taskmanager123"

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------- HOME ----------

@app.route("/")
def home():
    if "user_id" not in session:
        return render_template("index.html")

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect("/login")

    search = request.args.get("search", "")

    query = Task.query.filter_by(
        user_id=session["user_id"]
    )

    if search:
        query = query.filter(
            Task.title.contains(search)
        )

    tasks = query.all()

    completed = len(
        [t for t in tasks if t.status == "Completed"]
    )

    pending = len(
        [t for t in tasks if t.status == "Pending"]
    )

    total = len(tasks)

    progress = 0

    if total > 0:
        progress = round(
            (completed / total) * 100
        )

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress
    )


# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        try:
            existing_user = User.query.filter_by(
                username=request.form["username"]
            ).first()

            if existing_user:
                return redirect("/login")

            hashed_password = generate_password_hash(
                request.form["password"]
            )

            new_user = User(
                username=request.form["username"],
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect("/login")

        except Exception as e:
            return str(e)

    return render_template("signup.html")


# ---------- LOGIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and check_password_hash(
            user.password,
            request.form["password"]
        ):

            session["user_id"] = user.id

            return redirect("/")

    return render_template("login.html")


# ---------- ADD TASK ----------

@app.route("/add", methods=["POST"])
def add():

    if "user_id" not in session:
        return redirect("/login")

    task = Task(
        title=request.form.get("task"),
        description=request.form.get("description", ""),
        priority=request.form.get("priority", "Medium"),
        category=request.form.get("category", "General"),
        due_date=request.form.get("due_date", ""),
        user_id=session["user_id"]
    )

    db.session.add(task)
    db.session.commit()

    return redirect("/")


# ---------- COMPLETE TASK ----------

@app.route("/complete/<int:id>")
def complete(id):

    task = Task.query.get(id)

    if task:
        task.status = "Completed"
        db.session.commit()

    return redirect("/")


# ---------- DELETE TASK ----------

@app.route("/delete/<int:id>")
def delete(id):

    task = Task.query.get(id)

    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect("/")


# ---------- PROFILE ----------

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect("/login")

    tasks = Task.query.filter_by(
        user_id=user.id
    ).all()

    total = len(tasks)

    completed = len(
        [t for t in tasks if t.status == "Completed"]
    )

    pending = len(
        [t for t in tasks if t.status == "Pending"]
    )

    progress = 0

    if total > 0:
        progress = round(
            (completed / total) * 100
        )

    return render_template(
        "profile.html",
        user=user,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress
    )


# ---------- LOGOUT ----------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)