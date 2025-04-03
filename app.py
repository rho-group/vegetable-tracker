from flask import Flask, render_template, request, jsonify, Response, make_response
import matplotlib.pyplot as plt
import io
import os
import psycopg2
import datetime
import uuid
import matplotlib
from werkzeug.middleware.proxy_fix import ProxyFix

matplotlib.use('agg')


USER_ID = 1
selected_items = []
TARGET_VALUE = 30

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# DB connection in the Azure Database
'''
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

# Add new user to the database based on the cookies    
def add_user_to_db(username):
    """ Add new user if not exists """
    connection = create_connection(db_params)
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
                connection.commit()
        except Exception as error:
            print("Error inserting user:", error)
        finally:
            connection.close()

connection = create_connection(db_params)
cursor = connection.cursor()

# Get all vegetables available from the database
cursor.execute("SELECT foodname FROM vegetables;")
rows = cursor.fetchall()
vegetable_list = [row[0].capitalize() for row in rows]

# Get eaten history data from database for current user
def get_eaten_history_data(id):
    cursor.execute(f"SELECT distinct veg_id FROM eaten WHERE user_id = {id};")
    veg_ids = cursor.fetchall()
    
    for item in veg_ids:
        selected_items.append(vegetable_list[item[0]-1])

# Fetch user id from database based on the uuid username from cookies
def get_user_id_from_db(username):
    cursor.execute(f"SELECT id FROM users WHERE username = '{username}';")
    row = cursor.fetchone()

    if row is None:
        print('User not found')
        return None
    else:
        global USER_ID
        USER_ID = int(row[0])

    get_eaten_history_data(USER_ID)

@app.route("/get_cookie")
def get_cookie():
    """ check if user exists and adds if not """
    username = request.cookies.get('username')  # get cookie
    if username:
        print(username)
        return f'Welcome back, {username}!'
    if not username:
        # generate new username
        new_username = uuid.uuid4().hex[:32]

        # save to db
        add_user_to_db(new_username)

        # set cookie
        resp = make_response(f'New user created: {new_username}')
        resp.set_cookie('username', new_username, max_age=60*60*24*30, secure=True, samesite='None', httponly=True)
        print(new_username)
        return resp
    


@app.route('/')
def index():
    get_cookie()
    get_user_id_from_db(request.cookies.get('username'))
    return render_template('index.html')

# This route returns suggestions based on user input
@app.route('/suggest')
def suggest():
    query = request.args.get('q', '')
    suggestions = [veg for veg in vegetable_list if query.lower() in veg.lower()]
    return jsonify(suggestions)

# This route is for removing an item from the list
@app.route('/remove_item', methods=['DELETE'])
def remove_item():
    item = request.json.get('item')
    
    if item in selected_items:
        selected_items.remove(item)  # Remove from the server-side list
    
    print(f'ITEM DELETED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})

# Save selected vegetables to backend
@app.route('/save_items', methods=['POST'])
def save_items():
    items = request.json.get('items')
    current_timestamp = datetime.datetime.now()
    for item in items:
        #if item in selected_items:
        #    selected_items.remove(item)
        selected_items.append(item)
        cursor.execute("INSERT INTO eaten (user_id, veg_id, date) VALUES (%s, %s, %s);",(USER_ID,(vegetable_list.index(item)+1),current_timestamp))
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
    ax.bar("Your progress",current_value, color="lightgreen")
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
