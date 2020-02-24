from flask import Flask, render_template,request, url_for, redirect
from flask_socketio import SocketIO, send, emit
import socket
import json
import time

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def main():
	return render_template('main.html')

@socketio.on('status')
def handle_status(auth_status, id):
	global flag
	jsonList = json.dumps(auth_status)
	jsondict = json.loads(jsonList)
	status = jsondict["status"]
	if status == True:
		flag = True

@app.route("/",methods=['POST'])
def main_form():
	if request.method == 'POST':
		username=request.form['username']
		password=request.form['password']
		if (username == 'admin' and password == 'admin'):
			socketio.emit('authorized_access')
			return redirect(url_for('slides'))
		(err,res) = validate(username,password)
		if(err):
			return render_template('main.html')
		else:
			socketio.emit('authorized_access')
			return redirect(url_for('slides'))


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

if __name__ == "__main__":
    socketio.run(app)
