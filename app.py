import os
from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Try to load real Pinterest creds…
CLIENT_ID     = os.environ.get('PINTEREST_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PINTERST_CLIENT_SECRET')
REDIRECT_URI  = os.environ.get('PINTEREST_REDIRECT_URI')
SCOPE         = 'boards:read pins:read'

# Detect demo mode if any key creds are missing
DEMO_MODE = not (CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)

# Sample data for demo mode
DEMO_BOARDS = [
    {'id': 'demo1', 'name': 'My Favorite Recipes'},
    {'id': 'demo2', 'name': 'Travel Inspiration'},
]
DEMO_PINS = {
    'demo1': [
        {'id': 'pin1', 'note': 'Chocolate Cake', 'image_url': 'https://via.placeholder.com/200'},
        {'id': 'pin2', 'note': 'Pasta Salad',     'image_url': 'https://via.placeholder.com/200'},
    ],
    'demo2': [
        {'id': 'pin3', 'note': 'Paris at Night',  'image_url': 'https://via.placeholder.com/200'},
        {'id': 'pin4', 'note': 'Santorini Sunsets','image_url': 'https://via.placeholder.com/200'},
    ],
}

@app.route('/')
def index():
    return render_template('index.html', demo=DEMO_MODE)

@app.route('/login')
def login():
    if DEMO_MODE:
        # Skip OAuth and go straight to boards
        return redirect(url_for('boards'))
    # Real OAuth flow
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    url = 'https://api.pinterest.com/oauth/' + '?' + '&'.join(f"{k}={v}" for k, v in auth_params.items())
    return redirect(url)

@app.route('/callback')
def callback():
    if DEMO_MODE:
        return redirect(url_for('boards'))
    # Real token exchange…
    code = request.args.get('code')
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post('https://api.pinterest.com/v5/oauth/token',
                             data=payload, auth=(CLIENT_ID, CLIENT_SECRET))
    response.raise_for_status()
    session['access_token'] = response.json()['access_token']
    return redirect(url_for('boards'))

@app.route('/boards')
def boards():
    if DEMO_MODE:
        boards = DEMO_BOARDS
    else:
        headers = {'Authorization': f"Bearer {session['access_token']}"}
        res = requests.get('https://api.pinterest.com/v5/boards', headers=headers)
        res.raise_for_status()
        boards = res.json().get('items', [])
    return render_template('boards.html', boards=boards, demo=DEMO_MODE)

@app.route('/boards/<board_id>/pins')
def pins(board_id):
    if DEMO_MODE:
        pins = DEMO_PINS.get(board_id, [])
    else:
        headers = {'Authorization': f"Bearer {session['access_token']}"}
        params = {'limit': 50}
        res = requests.get(f'https://api.pinterest.com/v5/boards/{board_id}/pins',
                           headers=headers, params=params)
        res.raise_for_status()
        pins = res.json().get('items', [])
    return render_template('pins.html', pins=pins, board_id=board_id, demo=DEMO_MODE)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
