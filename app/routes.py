from flask import render_template, request
from app import app
from google.oauth2 import id_token
from google.auth.transport import requests

@app.route('/')
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate_user():
    user_data = request.form.to_dict()
    token = user_data.get('id_token')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), '90788619195-8910esr89h0eeogsdj28m9f59jk8iup7.apps.googleusercontent.com')
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        user_data['user_id'] = idinfo['sub']
    except ValueError as e:
        # Invalid user
        return str(e);
    
    # Valid user
    return 'The user is valid.'

@app.route('/ide')
def ide_page():
    return render_template('ide.html')

