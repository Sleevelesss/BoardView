import os
from flask import Flask, redirect, url_for, render_template, session, request

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# -- DEMO MODE: always use sample data --
DEMO_MODE = True

# Sample boards with your attached static images
DEMO_BOARDS = [
    {
        'id': 'demo1',
        'name': 'My Favorite Recipes',
        'image_url': '/static/recipes.png'
    },
    {
        'id': 'demo2',
        'name': 'Travel Inspiration',
        'image_url': '/static/travel.png'
    },
]

# Sample pins per board
DEMO_PINS = {
    'demo1': [
        {'id': 'pin1', 'note': 'Chocolate Cake',
         'image_url': 'https://via.placeholder.com/300x200?text=Chocolate+Cake'},
        {'id': 'pin2', 'note': 'Pasta Salad',
         'image_url': 'https://via.placeholder.com/300x200?text=Pasta+Salad'},
        {'id': 'pin3', 'note': 'Blueberry Muffins',
         'image_url': 'https://via.placeholder.com/300x200?text=Blueberry+Muffins'},
    ],
    'demo2': [
        {'id': 'pin4', 'note': 'Eiffel Tower at Night',
         'image_url': '/static/Eiffel'},
        {'id': 'pin5', 'note': 'Santorini Sunset',
         'image_url': 'https://via.placeholder.com/300x200?text=Santorini+Sunset'},
        {'id': 'pin6', 'note': 'Great Wall of China',
         'image_url': 'https://via.placeholder.com/300x200?text=Great+Wall+of+China'},
    ],
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    # In demo, skip OAuth and go straight to boards
    return redirect(url_for('boards'))

@app.route('/boards')
def boards():
    # Render our demo boards
    return render_template('boards.html', boards=DEMO_BOARDS)

@app.route('/boards/<board_id>/pins')
def pins(board_id):
    # Render demo pins for the chosen board
    pins = DEMO_PINS.get(board_id, [])
    return render_template('pins.html', pins=pins, board_id=board_id)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, host='0.0.0.0')
