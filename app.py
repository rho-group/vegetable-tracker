from flask import Flask, render_template, request, jsonify, Response,url_for, flash, redirect
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask import session


user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
name = os.getenv('DB_NAME')

matplotlib.use('agg')

#selected_items = []
TARGET_VALUE = 30

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
    
# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    eaten = db.relationship('Eaten', backref='user', lazy=True)

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
    foodgroup = db.Column(db.Integer, default=0)

    eaten = db.relationship('Eaten', backref='vegetable', lazy=True)

class Eaten(db.Model):
    __tablename__ = 'eaten'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    veg_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Season(db.Model):
    __tablename__ = 'inseason'
    id = db.Column(db.Integer, primary_key=True)
    veg_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'), nullable=False)
    jan = db.Column(db.Integer, default=0)
    feb = db.Column(db.Integer, default=0)
    mar = db.Column(db.Integer, default=0)
    apr = db.Column(db.Integer, default=0)
    may = db.Column(db.Integer, default=0)
    jun = db.Column(db.Integer, default=0)
    jul = db.Column(db.Integer, default=0)
    aug = db.Column(db.Integer, default=0)
    sep = db.Column(db.Integer, default=0)
    oct = db.Column(db.Integer, default=0)
    nov = db.Column(db.Integer, default=0)
    dec = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Get all vegetables available from the database
def get_vegetable_list():
    return [veg.foodname for veg in Vegetable.query.all()]

def get_eaten_history_data(id):
    # Haetaan veg_id:t eaten-taulusta käyttäjälle
    veg_ids = Eaten.query.filter_by(user_id=id).distinct(Eaten.veg_id).all()
 
    session['selected_items'] = []
 
    for item in veg_ids:
        vegetable = db.session.get(Vegetable, item.veg_id)
        if vegetable is not None:
            session['selected_items'].append(vegetable.foodname)

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


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            #user = User(username=username, password=password)
            login_user(user)
            session['selected_items'] = []
            print(f'LOGGED IN: Current username: {current_user.username}')
            print(f'LOGGED IN: Current user id: {current_user.id}')
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

            print(f'REGISTERED')
            flash("Account created successfully!", "success")

            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('selected_items', None)
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

    
@app.route('/home')
@login_required
def index():
    get_eaten_history_data(current_user.id)

    return render_template('index.html')


# This route returns suggestions based on user input
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

# This route is for removing an item from the list
@app.route('/remove_item', methods=['DELETE'])
@login_required
def remove_item():
    item = request.json.get('item')
    items = session.get('selected_items', [])

    if item in items:
        items.remove(item)
        session['selected_items'] = items
    return jsonify({'success': True, 'selected_items': items})

@app.route('/about')
def about():
    return render_template('about.html')


# Convert local datetime to UTC using zoneinfo
def convert_to_utc_now(user_timezone: str) -> datetime:
    try:
        local_tz = ZoneInfo(user_timezone)
        local_now = datetime.now(local_tz)
        utc_now = local_now.astimezone()
        return utc_now
    
    except Exception as e:
        raise ValueError(f"Timezone conversion failed: {e}")

# Save selected vegetables to backend
@app.route('/save_items', methods=['POST'])
@login_required
def save_items():
    items = request.json.get('items')
    user_timezone = request.json.get('timezone')

    if not user_timezone:
        return jsonify({'error': 'Timezone not provided'}), 400

    current_timestamp = convert_to_utc_now(user_timezone)

    current_selected = session.get('selected_items', [])

    for item in items:
            if item in current_selected:
                current_selected.remove(item)
            current_selected.append(item)

            veg = Vegetable.query.filter_by(foodname=item).first()
            if veg:
                new_eaten = Eaten(
                    user_id=current_user.id,
                    veg_id=veg.id,
                    date=current_timestamp.replace(tzinfo=ZoneInfo("UTC"))
                )
                db.session.add(new_eaten)

    db.session.commit()
    session['selected_items'] = current_selected

    print(f'ITEMS ADDED, selected list: {current_selected}')
    return jsonify({'success': True, 'selected_items': current_selected})


# Get eaten list to frontend
@app.route('/get_items', methods=['GET'])
def get_items():
    return jsonify(session.get('selected_items', []))

# Generate Stacked Bar Chart
@app.route('/get_bar_chart')
def get_bar_chart():
    current_value = len(session.get('selected_items', []))  # Number of selected items

    groups = {
        'Vegetables': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 1).count(),
        'Fruits': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 2).count(),
        'Berries': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 3).count(),
        'Nuts and seeds': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 4).count(),
        'Grain': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 5).count(),
        'Legume': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 6).count(),
        'Mushroom': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 7).count(),
        'Herb': Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', [])),Vegetable.foodgroup == 8).count()
    }

    custom_colors = [
        '#498743',  # vegetables
        '#aa026f',  # fruits
        '#e30c1a',  # berries
        '#f57a0e',  # nuts and seeds
        '#f8ad01',  # grain
        '#5c0029',  # legume
        '#927643',  # mushroom
        '#104b31',  # herb
    ]

    labels = list(groups.keys())
    values = list(groups.values())
    colors = custom_colors

    # Create the plot
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_alpha(0)
    bottom = 0
    
    for i in range(len(values)):
        ax.bar(' ', values[i], bottom=bottom, label=labels[i], color=colors[i])
        bottom += values[i]

    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax.axhline(y=TARGET_VALUE, color="green", linestyle="--", linewidth=1)
    ax.set_ylim(0, TARGET_VALUE + (TARGET_VALUE//6))
    ax.text(-0.28, current_value + 0.2, f"{current_value/30*100:.0f} % of your weekly goal!")
    plt.tight_layout()

    # Save plot to BytesIO buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close(fig)
    img.seek(0)

    return Response(img.getvalue(), mimetype='image/png')


# Get information about vitamins of eaten vegetables
@app.route('/get_vitamins')
def get_vitamins():
    vitamin_dictionary = {
        'calsium': 0, 'carotenoids': 0, 'iron': 0, 'fiber': 0, 'folate': 0,
        'iodine': 0, 'kalium': 0, 'magnesium': 0, 'niacin': 0, 'phosphorus': 0,
        'riboflavin': 0, 'selenium': 0, 'thiamin': 0, 'vitamina': 0, 'vitaminb12': 0,
        'vitaminc': 0, 'vitamind': 0, 'vitamink': 0, 'vitaminb6': 0, 'zinc': 0
    }

    # Query to get the selected vegetable records using SQLAlchemy ORM
    vegetables = Vegetable.query.filter(Vegetable.foodname.in_(session.get('selected_items', []))).all()

    # Update the vitamin dictionary based on the fetched data
    for vegetable in vegetables:
        for key in vitamin_dictionary.keys():
            if getattr(vegetable, key) > 0:
                vitamin_dictionary[key] = 1

    return jsonify(vitamin_dictionary)

@app.route('/get_vegetables_with_vitamin')
def get_vegetables_with_vitamin():
    vitamin = request.args.get('vitamin')

    if vitamin not in Vegetable.__table__.columns:
        return jsonify([])

    # Hae vihannekset joissa tämä vitamiini on arvoltaan > 0
    vegetables = Vegetable.query.filter(getattr(Vegetable, vitamin) > 0).all()
    names = [v.foodname.capitalize() for v in vegetables]

    return jsonify(names)

@app.route('/in_season')
def get_in_season_data():
    current_month = datetime.now().strftime("%b").lower()
    column = getattr(Season, current_month)
    in_season = (db.session.query(Vegetable.id, Vegetable.foodname)
    .join(Season, Vegetable.id == Season.veg_id)
    .filter(column == 1)
    .all())
    
    return jsonify({
        "in_season": [{"name": veg.foodname.capitalize()} for veg in in_season]
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

