from db import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(200), unique= True)
    password = db.Column(db.String(200))

class MsgStat(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    msg = db.Column(db.Text)
    label = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default= datetime.utcnow)