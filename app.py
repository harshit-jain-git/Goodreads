from flask import Flask, render_template,request, url_for, redirect
from flask_socketio import SocketIO, send, emit
import socket
import json
import time
import psycopg2

app = Flask(__name__,
			static_url_path='',
			static_folder='static',
			template_folder='templates')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def validate(username, passkey):
	query = "select count(user_id) from users where user_id = {} and password = '{}'".format(username, passkey)
	conn = psycopg2.connect("dbname=goodbooks user=postgres host=localhost port=5433 password=postgres")
	cur = conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	if (rows[0][0] == 1):
		print("LOGIN SUCCESSFULL!")
		return (False, None)
	else:
		print("INVALID CREDENTIALS!")
		return (True, None)

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
			return redirect(url_for('user_page'))
		(err,res) = validate(username,password)
		if(err):
			return render_template('main.html')
		else:
			socketio.emit('authorized_access')
			return redirect(url_for('user_page'))


@app.route('/<path:path>')
def static_file(path):
	return app.send_static_file(path)

if __name__ == "__main__":
	socketio.run(app)
