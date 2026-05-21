from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from models import db, User, Task


app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///database.db"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

app.secret_key = "taskmanager123"

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------- HOME ----------

@app.route("/")
def home():

    if "user_id" in session:

        tasks = Task.query.filter_by(
            user_id=session["user_id"]
        ).all()

        return render_template(
            "dashboard.html",
            tasks=tasks
        )

    return render_template(
        "index.html"
    )


# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        user = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if user:
            return redirect("/login")

        new_user = User(
            username=request.form["username"],
            password=request.form["password"]
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect("/login")

    return render_template(
        "signup.html"
    )


# ---------- LOGIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:

            session["user_id"] = user.id

            return redirect("/")

    return render_template(
        "login.html"
    )


# ---------- ADD TASK ----------

@app.route("/add", methods=["POST"])
def add():

    if "user_id" not in session:
        return redirect("/login")

    task = Task(
        title=request.form["task"],
        user_id=session["user_id"]
    )

    db.session.add(task)

    db.session.commit()

    return redirect("/")


# ---------- COMPLETE ----------

@app.route("/complete/<int:id>")
def complete(id):

    task = Task.query.get(id)

    if task:

        task.status = "Completed"

        db.session.commit()

    return redirect("/")


# ---------- DELETE ----------

@app.route("/delete/<int:id>")
def delete(id):

    task = Task.query.get(id)

    if task:

        db.session.delete(task)

        db.session.commit()

    return redirect("/")


# ---------- LOGOUT ----------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run()