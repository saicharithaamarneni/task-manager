from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    tasks = db.relationship(
        "Task",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Task(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    priority = db.Column(
        db.String(20),
        default="Medium"
    )

    category = db.Column(
        db.String(50),
        default="General"
    )

    due_date = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )