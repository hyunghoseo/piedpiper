from flask import render_template, request, url_for
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

def save_file(fname, program):
    with open(fname, 'w+') as f:
        to_write = ''
        for l in program.splitlines():
            to_write += l + '\n'
        f.write(to_write)

def compile_file(file_id, language):
    dirname = 'app/saved_files/{}'.format(file_id)
    fname = 'app/saved_files/{}.{}'.format(file_id, language)
    os.makedirs(dirname)
    if language == 'java':
        cmd = 'javac -d {} {}'.format(dirname, fname)
    elif fname.endswith('.swift'):
        pass
    else:
        print 'Unsupported language'
    subprocess.Popen(cmd, shell=True)
    
def run_file(file_id, language):
    return
    

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

@app.route('/ide/save/', methods=['POST'])
def save_code():
    file_id = request.form.get('id')
    language = request.form.get('language')
    program = request.form.get('program')
    
    fname = 'app/saved_files/{}.{}'.format(file_id, language)
    save_file(fname, program)
    
    return '200' #SUCCESS

@app.route('/ide/run/', methods=['POST'])
def run_code():
    file_id = request.form.get('id')
    language = request.form.get('language')
    program = request.form.get('program')
    
    fname = 'app/saved_files/{}.{}'.format(file_id, language)
    save_file(fname, program)
    compile_file(file_id, language)
    
    print program
    print file_id
    
    return '200' #SUCCESS