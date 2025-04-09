from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import os
#from dotenv import load_dotenv
#load_dotenv()

DB_USER="rhoAdmin"
DB_PASSWORD="ViliVihannes123"
DB_HOST="vegetable-tracker-db.postgres.database.azure.com"
DB_NAME="nutritions"
SECRET_KEY="salainen"

matplotlib.use('agg')

selected_items = []

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

# ----------- DATABASE MODELS -----------

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Vegetable(db.Model):
    __tablename__ = 'vegetables'
    id = db.Column(db.Integer, primary_key=True)
    foodname = db.Column(db.String(128), nullable=False)
    calsium = db.Column(db.Float)
    carotenoids = db.Column(db.Float)
    iron = db.Column(db.Float)
    fiber = db.Column(db.Float)
    folate = db.Column(db.Float)
    iodine = db.Column(db.Float)
    kalium = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    niacin = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    riboflavin = db.Column(db.Float)
    selenium = db.Column(db.Float)
    thiamin = db.Column(db.Float)
    vitamina = db.Column(db.Float)
    vitaminb12 = db.Column(db.Float)
    vitaminc = db.Column(db.Float)
    vitamind = db.Column(db.Float)
    vitamine = db.Column(db.Float)
    vitamink = db.Column(db.Float)
    vitaminb6 = db.Column(db.Float)
    zinc = db.Column(db.Float)

class Eaten(db.Model):
    __tablename__ = 'eaten'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    veg_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'))
    date = db.Column(db.DateTime)

# ----------- LOGIN MANAGER -----------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------- HELPERS -----------

def convert_to_utc_now(user_timezone: str) -> datetime:
    local_tz = ZoneInfo(user_timezone)
    local_now = datetime.now(local_tz)
    return local_now.astimezone(ZoneInfo("UTC"))

def suggest_vitamins(veg_name):
    vitamin_keys = [
        'calsium', 'carotenoids', 'iron', 'fiber', 'folate', 'iodine', 'kalium',
        'magnesium', 'niacin', 'phosphorus', 'riboflavin', 'selenium', 'thiamin',
        'vitamina', 'vitaminb12', 'vitaminc', 'vitamind', 'vitamine', 'vitamink',
        'vitaminb6', 'zinc'
    ]
    result = dict.fromkeys(vitamin_keys, 0)
    veg = Vegetable.query.filter_by(foodname=veg_name).first()
    if veg:
        for key in vitamin_keys:
            if getattr(veg, key):
                result[key] = 1
    return result

# ----------- ROUTES -----------

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
            return redirect(url_for('login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created!", "success")
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
    selected_items.clear()
    global USER_ID
    USER_ID = current_user.id
    get_eaten_history_data(USER_ID)

    return render_template('index.html', items=selected_items)


@app.route('/suggest')
@login_required
def suggest():
    query = request.args.get('q', '').lower()
    matches = Vegetable.query.filter(Vegetable.foodname.ilike(f"%{query}%")).all()
    results = []

    for veg in matches:
        vitas = suggest_vitamins(veg.foodname)
        vitas = [k for k, v in vitas.items() if v == 1]
        results.append({'vegetable': veg.foodname, 'vitamins': vitas})

    return jsonify(results)

@app.route('/save_items', methods=['POST'])
@login_required
def save_items():
    data = request.get_json()
    items = data.get('items', [])
    tz = data.get('timezone', 'UTC')
    timestamp = convert_to_utc_now(tz)

    for name in items:
        veg = Vegetable.query.filter_by(foodname=name).first()
        if veg:
            db.session.add(Eaten(user_id=current_user.id, veg_id=veg.id, date=timestamp))
    db.session.commit()
    return jsonify({'success': True})

@app.route('/get_bar_chart')
def get_bar_chart():
    count = Eaten.query.filter_by(user_id=current_user.id).count()
    fig, ax = plt.subplots()
    ax.bar('Vegetables', count, color='green')
    ax.axhline(30, color='red', linestyle='--')
    ax.text(0, count + 1, f"{count/30*100:.0f}% of your weekly goal!")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return Response(buf.getvalue(), mimetype='image/png')

@app.route('/get_vitamins')
@login_required
def get_vitamins():
    eaten_veg_ids = db.session.query(Eaten.veg_id).filter_by(user_id=current_user.id).distinct()
    vitamins = dict.fromkeys([
        'calsium','carotenoids','iron','fiber','folate','iodine','kalium','magnesium','niacin','phosphorus',
        'riboflavin','selenium','thiamin','vitamina','vitaminb12','vitaminc','vitamind','vitamine',
        'vitamink','vitaminb6','zinc'
    ], 0)

    vegs = Vegetable.query.filter(Vegetable.id.in_([vid for (vid,) in eaten_veg_ids])).all()

    for veg in vegs:
        for k in vitamins:
            if getattr(veg, k):
                vitamins[k] = 1
    return jsonify(vitamins)

@app.route('/add_item', methods=['POST'])
def add_item():
    item = request.json.get('item')
    if item and item not in selected_items:
        selected_items.append(item)  # Add to the server-side list
    print(f'ITEM ADDED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})

# Get eaten list to frontend
@app.route('/get_items', methods=['GET'])
def get_items():
    return jsonify(selected_items)

@app.route('/get_eaten_history/<int:id>', methods=['GET'])
def get_eaten_history_data(id):
    # Haetaan veg_id:t eaten-taulusta käyttäjälle
    veg_ids = Eaten.query.filter_by(user_id=id).distinct(Eaten.veg_id).all()

    selected_items = []

    for item in veg_ids:
        vegetable = Vegetable.query.get(item.veg_id)  # Haetaan vihannes tietokannasta veg_id:n perusteella
        if vegetable:
            selected_items.append({'id': vegetable.id, 'name': vegetable.foodname})

    return jsonify(selected_items)


# ------------

if __name__ == "__main__":
    app.run(debug=True)
