from flask import render_template, request, url_for, redirect, session, jsonify
from app import app, sio
from google.oauth2 import id_token
from google.auth.transport import requests
from pusher import Pusher
import json, os, subprocess, time
import db
import datetime

db.createdb()

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
    user_id = session['user_data']['user_id']
    dirname = 'app/saved_files/{}/{}'.format(user_id, file_id)
    fname = 'app/saved_files/{}/{}.{}'.format(user_id, file_id, language)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if language == 'java':
        cmd = 'javac -d {} {}'.format(dirname, fname)
    elif fname.endswith('.swift'):
        pass
    else:
        print 'Unsupported language'
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = pipe.communicate()
    if error:
        return error
    
def run_file(file_id, language, u_input):
    dirname = 'app/saved_files/{}/{}'.format(session['user_data']['user_id'], file_id)
    oldpath = os.getcwd()
    os.chdir(dirname)
    if language == 'java':
        if u_input:
            cmd = 'echo "{}" | java {}'.format(u_input, file_id)
        else:
            cmd = 'java {}'.format(file_id)
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = pipe.communicate()
    os.chdir(oldpath)
    if error:
        return error
    return output
    
@app.route('/home/', methods=['GET'])
def home():
    if not session.get('registered'):
        return redirect(url_for('index'))
    return render_template('HomePage.html', user = session['user_data']['first_name'])

@app.route('/')
@app.route('/index/', methods=['GET'])
def index():
    if session.get('registered'):
        return redirect(url_for('home'))
    return render_template('LandingPage.html')

@app.route('/login/', methods=['POST'])
def authenticate_user():
    user_data = request.form.to_dict()
    token = user_data.get('id_token')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), '90788619195-8910esr89h0eeogsdj28m9f59jk8iup7.apps.googleusercontent.com')
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
            
        user_data['user_id'] = idinfo['sub']
        
        session['user_data'] = user_data

        if db.check_if_user_exists(user_data['user_id']):
            session['registered'] = True
            return 'registered'
        else:
            session['registered'] = False
            return 'unregistered'

    except ValueError as e:
        # Invalid user
        return str(e);
    
    # Valid user
    return 'error'

@app.route('/logout/', methods=['POST'])
def logout():
    session.pop('user_data', None)
    session.pop('registered', None)
    return "200"

@app.route('/register/', methods=['POST'])
def register():
    if session.get('registered'):
        return redirect(url_for('home'))

    accounttype = int( request.form.get('accounttype') )

    user_data = session['user_data']
    
    db.insert_new_user(
        user_data['user_id'],
        user_data['first_name'],
        user_data['last_name'],
        user_data['email'],
        user_data['image_url'],
        accounttype
    )
    session['registered'] = True                
    
    return "200"


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
    
    dirname = 'app/saved_files/{}'.format(session['user_data']['user_id'])
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
    fname = 'app/saved_files/{}/{}.{}'.format(session['user_data']['user_id'], file_id, language)
    save_file(fname, program)
    
    return '200' #SUCCESS

@app.route('/ide/run/', methods=['POST'])
def run_code():
    file_id = request.form.get('id')
    language = request.form.get('language')
    program = request.form.get('program')
    u_input = request.form.get('input')
    
    dirname = 'app/saved_files/{}'.format(session['user_data']['user_id'])
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
    fname = 'app/saved_files/{}/{}.{}'.format(session['user_data']['user_id'], file_id, language)
    save_file(fname, program)
    compile_err = compile_file(file_id, language)
    time.sleep(3)
    if compile_err:
        return complile_err
    output = run_file(file_id, language, u_input)
    
    return output

@app.route('/ide/getfiles/', methods=['POST'])
def get_files():
    dirname = 'app/saved_files/{}/'.format(session['user_data']['user_id'])
    onlyfiles = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dirname):
        files.extend(filenames)
        break
    return jsonify(files)

@app.route('/ide/open/', methods=['POST'])
def get_file_content():
    filename = request.form.get('filename')
    
    fname = 'app/saved_files/{}/{}'.format(session['user_data']['user_id'], filename)
    with open(fname, 'r') as f:
        return f.read()


connected_particpants = {}

def write_log(s):    
    with open('logfile.out', 'a+') as f:
        f.write('time: %s Action: %s \n' % (str(datetime.datetime.now()), s))

@app.route('/room/')
def default_room():
    if not session.get('registered'):
        return redirect(url_for('index'))
    return render_template('RoomPage.html', room='default', user=session['user_data']['first_name'])

@sio.on('message', namespace='/')
def messgage(sid, data):
    sio.emit('message', data=data)

@sio.on('disconnect', namespace='/')
def disconnect(sid):
    write_log("Received Disconnect message from %s" % sid)
    for room, clients in connected_particpants.iteritems():
        try:
            clients.remove(sid)
            write_log("Removed %s from %s \n list of left participants is %s" %(sid, room, clients))
        except ValueError:
            write_log("Remove %s from %s \n list of left participants is %s has failed" %(sid, room, clients))

@sio.on('create or join', namespace='/')
def create_or_join(sid, data):
    sio.enter_room(sid, data)
    try:
        connected_particpants[data].append(sid)
    except KeyError:
        connected_particpants[data] = [sid]
    numClients = len(connected_particpants[data])
    if numClients == 1:
        sio.emit('created', data)
    elif numClients == 2:
        sio.emit('joined')
        sio.emit('join')
    print (sid, data, len(connected_particpants[data]))

@app.route('/room/<room>/')
def room(room):
    if not session.get('registered'):
        return redirect(url_for('index'))
    return render_template('RoomPage.html', room=room, user=session['user_data']['first_name'])
