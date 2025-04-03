from flask import Flask, render_template, request, jsonify, Response, make_response,url_for, flash, redirect
import matplotlib.pyplot as plt
import io
import os
import psycopg2
import datetime
import uuid
import matplotlib
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt


matplotlib.use('agg')

USER_ID = 1
selected_items = []
TARGET_VALUE = 30

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
bcrypt = Bcrypt(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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
login_manager.login_view = "login"

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
vegetable_list = [row[0].capitalize() for row in rows]


@login_manager.user_loader
def load_user(user_id):
    cur = connection.cursor()
    cur.execute("SELECT id, username FROM users2 WHERE id = %s", (user_id,))
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
        cur.execute("SELECT id, username, password FROM users2 WHERE username = %s", (username,))
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
            cur.execute("SELECT id FROM users2 WHERE username = %s", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Username already exists!", "danger")
                return redirect(url_for('signup'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("INSERT INTO users2 (username, password) VALUES (%s, %s) RETURNING id", (username, hashed_password))
            user_id = cur.fetchone()[0]
            connection.commit()

            user = User(user_id, username)
            login_user(user)
            print(f'REGISTERED: Current username: {current_user.username}')
            print(f'REGISTERED: Current user id: {current_user.id}')
            flash("Account created successfully!", "success")
            return redirect(url_for('index'))

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
    cursor.execute(f"SELECT distinct veg_id FROM eaten2 WHERE user_id = {id};")
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
    return jsonify(suggestions)

# This route is for removing an item from the list
@app.route('/remove_item', methods=['DELETE'])
@login_required
def remove_item():
    item = request.json.get('item')
    
    if item in selected_items:
        selected_items.remove(item)  # Remove from the server-side list
    
    print(f'ITEM DELETED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})

# Save selected vegetables to backend
@app.route('/save_items', methods=['POST'])
@login_required
def save_items():
    items = request.json.get('items')
    current_timestamp = datetime.datetime.now()
    for item in items:
        #if item in selected_items:
        #    selected_items.remove(item)
        selected_items.append(item)
        cursor.execute("INSERT INTO eaten2 (user_id, veg_id, date) VALUES (%s, %s, %s);",(USER_ID,(vegetable_list.index(item)+1),current_timestamp))
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


if __name__ == '__main__':
    app.run(debug=True)

    cursor.close()
    connection.close()
