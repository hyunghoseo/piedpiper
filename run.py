from app import app, sio
import socketio, eventlet
#app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)
app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
