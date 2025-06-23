import os
from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change_me')

# Pinterest API endpoints
oauth_url = 'https://api.pinterest.com/oauth/'
token_url = 'https://api.pinterest.com/v5/oauth/token'
api_base = 'https://api.pinterest.com/v5/'

# Only read scopes for review: list boards and pins
CLIENT_ID = os.environ['PINTEREST_CLIENT_ID']
CLIENT_SECRET = os.environ['PINTEREST_CLIENT_SECRET']
REDIRECT_URI = os.environ.get('PINTEREST_REDIRECT_URI', 'https://your-domain.com/callback')
SCOPE = 'boards:read pins:read'

@app.route('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('boards'))
    return render_template('index.html')

@app.route('/login')
def login():
    # Redirect user to Pinterest OAuth
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    url = oauth_url + '?' + '&'.join(f"{k}={v}" for k, v in auth_params.items())
    return redirect(url)

@app.route('/callback')
def callback():
    # Exchange code for access token
    code = request.args.get('code')
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(token_url, data=payload, auth=(CLIENT_ID, CLIENT_SECRET))
    response.raise_for_status()
    session['access_token'] = response.json()['access_token']
    return redirect(url_for('boards'))

@app.route('/boards')
def boards():
    # Fetch and display user boards
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    res = requests.get(f"{api_base}boards", headers=headers)
    res.raise_for_status()
    boards = res.json().get('items', [])
    return render_template('boards.html', boards=boards)

@app.route('/boards/<board_id>/pins')
def pins(board_id):
    # Fetch and display pins on a board
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    params = {'limit': 50}
    res = requests.get(f"{api_base}boards/{board_id}/pins", headers=headers, params=params)
    res.raise_for_status()
    pins = res.json().get('items', [])
    return render_template('pins.html', pins=pins, board_id=board_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')