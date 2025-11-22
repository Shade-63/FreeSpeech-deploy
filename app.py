from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import db
from model import analyze_text
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, MsgStat
import plotly.graph_objs as go
import plotly.io as pio
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# DB config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///safespeak.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods= ["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)

        user = User(username= username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods= ["GET", "POST"])
def login():
    if request.method== "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username= username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/analyze", methods= ["POST"])
@login_required
def analyze():
    data = request.get_json()
    text = data.get("message", "").strip()

    if not text:
        return jsonify({"error" : "EMpty msg"}), 400
    
    result = analyze_text(text)
    score = result["primary_score"]

    if score>0.8:
        severity = "high"
    elif score>0.5:
        severity = "medium"
    else:
        severity = "low"

    stat = MsgStat(
        user_id = current_user.id,
        msg = text,
        label = result["primary_label"],
        severity= severity,
        score=score,
    )
    db.session.add(stat)
    db.session.commit()

    return jsonify({
        "message": text,
        "label": result["primary_label"],
        "severity": severity,
        "score": round(score * 100, 2),
        "all_scores": result["all_scores"]
    })

@app.route("/dashboard")
@login_required
def dashboard():
    stats = MsgStat.query.filter_by(user_id=current_user.id).all()

    total = len(stats)
    toxic = len([s for s in stats if s.severity != "low"])
    safe = total - toxic

    # ---------------- PIE CHART ----------------
    pie_labels = ["Safe", "Toxic"]
    pie_values = [safe, toxic]
    pie_colors = ['#28a745', '#dc3545']

    pie_chart = go.Figure(
        data=[go.Pie(
            labels=pie_labels,
            values=pie_values,
            hole=0.45,
            marker=dict(colors=pie_colors),
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            textposition='inside'
        )]
    )

    pie_chart.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    pie_html = pio.to_html(pie_chart, full_html=False, include_plotlyjs=False, config={'displayModeBar': False})

    # ---------------- BAR CHART ----------------
    label_counts = {}
    for s in stats:
        if s.severity != "low":  # Only count toxic messages for bar chart
            label_counts[s.label] = label_counts.get(s.label, 0) + 1

    # If no toxic messages, create empty chart
    if not label_counts:
        label_counts = {"No toxic messages": 1}
        
    bar_chart = go.Figure([
        go.Bar(
            x=list(label_counts.keys()), 
            y=list(label_counts.values()),
            marker_color='#1a73e8'
        )
    ])

    bar_chart.update_layout(
        height=350,
        margin=dict(l=60, r=20, t=40, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Toxicity Labels",
        yaxis_title="Count",
        font=dict(size=12)
    )

    bar_html = pio.to_html(bar_chart, full_html=False, include_plotlyjs=False, config={'displayModeBar': False})

    # ---------------- LINE CHART ----------------
    stats_sorted = sorted(stats, key=lambda x: x.timestamp)
    
    if stats_sorted:
        line_scores = [s.score for s in stats_sorted]
        line_time = [s.timestamp.strftime("%H:%M:%S") for s in stats_sorted]
    else:
        line_scores = [0]
        line_time = ["No data"]

    line_chart = go.Figure([
        go.Scatter(
            x=line_time, 
            y=line_scores, 
            mode='lines+markers',
            line=dict(color='#1a73e8', width=3),
            marker=dict(size=6)
        )
    ])

    line_chart.update_layout(
        height=350,
        margin=dict(l=60, r=20, t=40, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Time",
        yaxis_title="Toxicity Score",
        font=dict(size=12)
    )

    line_html = pio.to_html(line_chart, full_html=False, include_plotlyjs=False, config={'displayModeBar': False})

    # ---------------- RECENT TOXIC TABLE ----------------
    recent_toxic = (
        MsgStat.query.filter_by(user_id=current_user.id)
        .filter(MsgStat.severity != "low")
        .order_by(MsgStat.timestamp.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "dashboard.html",
        pie_chart=pie_html,
        bar_chart=bar_html,
        line_chart=line_html,
        recent_toxic=recent_toxic,
        total=total,
        toxic=toxic,
        safe=safe
    )

if __name__ == "__main__":
    app.run(debug=True)