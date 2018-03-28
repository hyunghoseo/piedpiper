from flask import render_template, request
from app import app
from google.oauth2 import id_token
from google.auth.transport import requests
from pusher import Pusher
import json, os, subprocess

pusher_client = Pusher(
    app_id='497667',
    key='b240a449c3e79c81f151',
    secret='9d88d88cc785f7f4f72b',
    cluster='us2',
    ssl=True
)

def compile_file(fname, language):
    if language == 'java':
        cmd = 'javac {}'.format(fname)
    elif language == 'swift':
        pass
    else:
        print 'Unsupported language'
    subprocess.Popen(cmd, shell=True)

@app.route('/')
@app.route('/login/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login/', methods=['POST'])
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

@app.route('/ide/')
def ide_page():
    return render_template('ide.html')

@app.route('/pusher/auth/', methods=['POST'])
def pusher_authentication():

  auth = pusher_client.authenticate(
    channel=request.form['channel_name'],
    socket_id=request.form['socket_id'],
    custom_data={
      u'user_id': u'1',
      u'user_info': {
        u'twitter': u'@pusher'
      }
    }
  )
  return json.dumps(auth)

@app.route('/ide/compile/', methods=['POST'])
def compile_code():
    file_id = request.form.get('id')
    language = request.form.get('language')
    program = request.form.get('program')
    
    fname = 'app/saved_files/{}.{}'.format(file_id, language)
    with open(fname, 'w+') as f:
        to_write = ''
        for l in program.splitlines():
            to_write += l + '\n'
        f.write(to_write)
        
    compile_file(fname, language)
    
    print program
    print file_id