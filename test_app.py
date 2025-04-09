from flask import Flask, render_template, request, jsonify, Response, url_for, flash, redirect
import matplotlib.pyplot as plt
import io
import os
import matplotlib
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

matplotlib.use('agg')

USER_ID = 1
selected_items = []
TARGET_VALUE = 30

# Initialize Flask app and other extensions
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

# Define database models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Vegetable(db.Model):
    __tablename__ = 'vegetables'
    id = db.Column(db.Integer, primary_key=True)
    foodname = db.Column(db.String(100), nullable=False, unique=True)
    calsium = db.Column(db.Integer, default=0)
    carotenoids = db.Column(db.Integer, default=0)
    iron = db.Column(db.Integer, default=0)
    fiber = db.Column(db.Integer, default=0)
    folate = db.Column(db.Integer, default=0)
    iodine = db.Column(db.Integer, default=0)
    kalium = db.Column(db.Integer, default=0)
    magnesium = db.Column(db.Integer, default=0)
    niacin = db.Column(db.Integer, default=0)
    phosphorus = db.Column(db.Integer, default=0)
    riboflavin = db.Column(db.Integer, default=0)
    selenium = db.Column(db.Integer, default=0)
    thiamin = db.Column(db.Integer, default=0)
    vitamina = db.Column(db.Integer, default=0)
    vitaminb12 = db.Column(db.Integer, default=0)
    vitaminc = db.Column(db.Integer, default=0)
    vitamind = db.Column(db.Integer, default=0)
    vitamine = db.Column(db.Integer, default=0)
    vitamink = db.Column(db.Integer, default=0)
    vitaminb6 = db.Column(db.Integer, default=0)
    zinc = db.Column(db.Integer, default=0)

class Eaten(db.Model):
    __tablename__ = 'eaten'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    veg_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Get all vegetables available from the database
def get_vegetable_list():
    return [veg.foodname for veg in Vegetable.query.all()]

def suggest_vitamins(veg_name):
    vit_dict = {
        'calsium': 0, 'carotenoids': 0, 'iron': 0, 'fiber': 0,
        'folate': 0, 'iodine': 0, 'kalium': 0, 'magnesium': 0,
        'niacin': 0, 'phosphorus': 0, 'riboflavin': 0, 'selenium': 0,
        'thiamin': 0, 'vitamina': 0, 'vitaminb12': 0, 'vitaminc': 0,
        'vitamind': 0, 'vitamink': 0, 'vitaminb6': 0, 'zinc': 0 }

    vegetable = Vegetable.query.filter_by(foodname=veg_name.upper()).first()

    if vegetable:
        for key in vit_dict.keys():
            if getattr(vegetable, key) > 0:
                vit_dict[key] = 1

    return vit_dict

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def index():
    global USER_ID
    USER_ID = current_user.id
    return render_template('index.html')

@app.route('/suggest')
@login_required
def suggest():
    query = request.args.get('q', '')
    suggestions = [veg for veg in get_vegetable_list() if query.lower() in veg.lower()]

    vitamins_info = []
    for veg in suggestions:
        vitamins_info.append({
            "vegetable": veg,
            "vitamins": [key for key, value in suggest_vitamins(veg).items() if value == 1]
        })

    return jsonify(vitamins_info)

# More routes can be added following the same pattern...

if __name__ == '__main__':
    app.run(debug=True)
