from flask import Flask, render_template, request, jsonify, Response
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# DB connection

# get this from db
vegetable_list = ['Carrot', 'Potato', 'Tomato', 'Cucumber', 'Spinach', 'Broccoli', 'Onion']

# Server-side list that stores selected items
selected_items = []
TARGET_VALUE = 30

@app.route('/')
def index():
    return render_template('index.html')

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

    for item in items:
        #if item in selected_items:
        #    selected_items.remove(item)
        selected_items.append(item)

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
