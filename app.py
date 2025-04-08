from flask import Flask, render_template, request, jsonify, Response,url_for, flash, redirect
import matplotlib.pyplot as plt
import io
import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import pandas as pd


matplotlib.use('agg')

USER_ID = 1
selected_items = []
TARGET_VALUE = 30

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
bcrypt = Bcrypt(app)


# DB connection in the Azure Database

db_params = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port':'5432'
}
'''
# DB connection locally for testing

db_params = {
    'host': "vegetable-tracker-db.postgres.database.azure.com",
    'user': "rhoAdmin",
    'password': "ADD",
    'database': "nutritions",
    'port':'5432'
}
'''

# Connect to database
def create_connection(db_params):
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(
            dbname=db_params['database'],
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port']
        )
        return connection
    except Exception as error:
        print(error)
        return None
    
# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
    def get_id(self):
        return self.id

connection = create_connection(db_params)
cursor = connection.cursor()

# Get all vegetables available from the database
cursor.execute("SELECT foodname FROM vegetables;")
rows = cursor.fetchall()
vegetable_list = [row[0] for row in rows]


query = """
SELECT foodname, calsium, carotenoids, iron, fiber, 
folate, iodine, kalium, magnesium, niacin, phosphorus, riboflavin, selenium, thiamin, vitamina, 
vitaminb12, vitaminc, vitamind, vitamine, vitamink, vitaminb6, zinc
FROM vegetables;
"""

veg_df = pd.read_sql(query, connection)

def suggest_vitamins(veg_name):
    vit_dict = {
    'calsium': 0, 'carotenoids': 0, 'iron': 0, 'fiber': 0,
    'folate': 0, 'iodine': 0, 'kalium': 0, 'magnesium': 0,
    'niacin': 0, 'phosphorus': 0, 'riboflavin': 0, 'selenium': 0,
    'thiamin': 0, 'vitamina': 0, 'vitaminb12': 0, 'vitaminc': 0,
    'vitamind': 0, 'vitamink': 0, 'vitaminb6': 0, 'zinc': 0 }

    veg_name.upper()

    single_df = veg_df[veg_df['foodname'] == veg_name]

    for key, value in vit_dict.items():
        if single_df[key].any():
            vit_dict[key] = 1

    return vit_dict


@login_manager.user_loader
def load_user(user_id):
    cur = connection.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()

    if user_data:
        return User(user_data[0], user_data[1])
    return None




@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = connection.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()

        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1])
            login_user(user)
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

            cur = connection.cursor()
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Username already exists!", "danger")
                return redirect(url_for('/'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id", (username, hashed_password))
            
            connection.commit()

            print(f'REGISTERED')
            flash("Account created successfully!", "success")

            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    selected_items.clear()
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

# Get eaten history data from database for current user
def get_eaten_history_data(id):
    cursor.execute(f"SELECT distinct veg_id FROM eaten WHERE user_id = {id};")
    veg_ids = cursor.fetchall()
    
    for item in veg_ids:
        selected_items.append(vegetable_list[item[0]-1])

    
@app.route('/home')
@login_required
def index():
    selected_items.clear()
    global USER_ID
    USER_ID = current_user.id
    get_eaten_history_data(USER_ID)

    return render_template('index.html')


# This route returns suggestions based on user input
@app.route('/suggest')
@login_required
def suggest():
    query = request.args.get('q', '')
    suggestions = [veg for veg in vegetable_list if query.lower() in veg.lower()]

    if suggestions:
        vitamins_info = {}
        suggestion_vitamin = []
        for veg in suggestions:
            vitamins_info[veg] = {key: value for key, value in suggest_vitamins(veg).items() if value == 1}
        
        for vegetable, vitamin in vitamins_info.items():
            vitamins_list = list(vitamin.keys())

            suggestion_vitamin.append({"vegetable": vegetable, "vitamins": vitamins_list})


    return jsonify(suggestion_vitamin)

# This route is for removing an item from the list
@app.route('/remove_item', methods=['DELETE'])
@login_required
def remove_item():
    item = request.json.get('item')
    
    if item in selected_items:
        selected_items.remove(item)  # Remove from the server-side list
    
    print(f'ITEM DELETED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})


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

    for item in items:
        if item in selected_items:
            selected_items.remove(item)
        selected_items.append(item)

        current_timestamp = current_timestamp.replace(tzinfo=ZoneInfo("UTC"))

        cursor.execute("INSERT INTO eaten (user_id, veg_id, date) VALUES (%s, %s, %s);",
                       (USER_ID,(vegetable_list.index(item) + 1),current_timestamp))

        connection.commit()
    print(f'ITEMS ADDED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})

# Get eaten list to frontend
@app.route('/get_items', methods=['GET'])
def get_items():
    return jsonify(selected_items)

# Generate Stacked Bar Chart
@app.route('/get_bar_chart')
def get_bar_chart():
    current_value = len(selected_items)  # Number of selected items

    fig, ax = plt.subplots(figsize=(5, 4))

    #ax.set_title(f"{current_value/30*100:.0f} % of your weekly goal!")
    ax.text(-0.2, current_value + 0.2, f"{current_value/30*100:.0f} % of your weekly goal!")

    # Create a stacked bar: First part is the actual count, second is the remaining space
    ax.bar(" ",current_value, color="lightgreen")
    ax.axhline(y=TARGET_VALUE, color="green", linestyle="--", linewidth=1)

    ax.set_ylim(0, TARGET_VALUE + (TARGET_VALUE//3))

    # Save plot to a bytes buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close(fig)
    img.seek(0)

    return Response(img.getvalue(), mimetype='image/png')

# Get information about vitamins of eaten vegetables
@app.route('/get_vitamins')
def get_vitamins():
    vitamin_dictionary = {
        'calsium':0,
        'carotenoids':0,
        'iron':0,
        'fiber':0,
        'folate':0,
        'iodine':0,
        'kalium':0,
        'magnesium':0,
        'niacin':0,
        'phosphorus':0,
        'riboflavin':0,
        'selenium':0,
        'thiamin':0,
        'vitamina':0,
        'vitaminb12':0,
        'vitaminc':0,
        'vitamind':0,
        'vitamink':0,
        'vitaminb6':0,
        'zinc':0
    }
    query = """
    SELECT foodname, calsium, carotenoids, iron, fiber, 
    folate, iodine, kalium, magnesium, niacin, phosphorus, riboflavin, selenium, thiamin, vitamina, 
    vitaminb12, vitaminc, vitamind, vitamine, vitamink, vitaminb6, zinc
    FROM vegetables
    WHERE foodname = ANY(%s)
    """
    df = pd.read_sql(query, connection, params=(selected_items,))

    for key, value in vitamin_dictionary.items():
        if df[key].any():
            vitamin_dictionary[key] = 1

    return vitamin_dictionary

if __name__ == '__main__':
    app.run(debug=True)

    cursor.close()
    connection.close()
