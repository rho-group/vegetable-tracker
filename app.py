from flask import Flask, render_template, request, jsonify, Response, make_response
import matplotlib.pyplot as plt
import io
import os
import psycopg2
import datetime
import uuid

app = Flask(__name__)

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
    'host': "ADD",
    'user': "ADD",
    'password': "ADD",
    'database': "nutritions",
    'port':'5432'
}
'''
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

cursor.execute("SELECT foodname FROM vegetables;")
rows = cursor.fetchall()
vegetable_list = [row[0].capitalize() for row in rows]

# get this from db
#vegetable_list = ['Carrot', 'Potato', 'Tomato', 'Cucumber', 'Spinach', 'Broccoli', 'Onion']
selected_items = []
# Server-side list that stores selected items
#Select all eaten items for the static user.
cursor.execute("SELECT distinct veg_id FROM eaten WHERE user_id = 1;")
veg_ids = cursor.fetchall()
for item in veg_ids:
    selected_items.append(vegetable_list[item[0]-1])

TARGET_VALUE = 30

@app.route('/')
def index():
    get_cookie()

    return render_template('index.html')

#@app.route('/set_cookie')
def set_cookie():
    """ Create new user set cookie. """
    new_username = uuid.uuid4().hex[:32]
    add_user_to_db(new_username)

    resp = make_response("Cookie has been set!")
    resp.set_cookie('username', new_username, max_age=60*60*24*30)#Cookie valid for 30 days return resp
    return resp

#@app.route('/get_cookie')
def get_cookie():
    """ check if user exists and adds if not """
    username = request.cookies.get('username')  # get cookie
    if username:
        print(username)
    if not username:
        # generate new username
        new_username = uuid.uuid4().hex[:32]

        # save to db
        add_user_to_db(new_username)

        # set cookie
        resp = make_response(f'New user created: {new_username}')
        resp.set_cookie('username', new_username, max_age=60*60*24*30)
        print(new_username)
        return resp

    return f'Welcome back, {username}!'

# This route returns suggestions based on user input
@app.route('/suggest')
def suggest():
    query = request.args.get('q', '')
    suggestions = [veg for veg in vegetable_list if query.lower() in veg.lower()]
    return jsonify(suggestions)

# This route is for adding an item to the list
@app.route('/add_item', methods=['POST'])
def add_item():
    item = request.json.get('item')
    if item and item not in selected_items:
        selected_items.append(item)  # Add to the server-side list
    print(f'ITEM ADDED, selected list: {selected_items}')
    return jsonify({'success': True, 'selected_items': selected_items})

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
        cursor.execute("INSERT INTO eaten (user_id, veg_id, date) VALUES (%s, %s, %s);",(1,(vegetable_list.index(item)+1),current_timestamp))
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
