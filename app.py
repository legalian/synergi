from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
import requests
# from flask.ext.heroku import Heroku
import os


app = Flask(__name__)
socketio = SocketIO(app)
# heroku = Heroku(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']



from models import Session, TemFile




@app.route("/projectlist")
def projectlist():
	return render_template('todolist.html')

@app.route("/editor")
def editor():
	return render_template('editor.html')

@app.route("/login")
def login():
	return redirect("https://github.com/login/oauth/authorize?scope=repo&client_id="+CLIENT_ID, code=302)



@app.route("/logout")
def logout():
	return "jw9ejfoweufj"


@app.route("/gitcallback")
def gitcallback():
	session_code = request.args.get('code')
	res = requests.post('https://github.com/login/oauth/access_token',params={'accept':'json'},data={'client_id':CLIENT_ID,'client_secret':CLIENT_SECRET,'code':session_code})
	res = res.json()
	print(res)
	access_token = res['access_token']
	user = User(
		path = request.json['path'],
		content = con['content'],
		sha = con['sha']
	)
	db.session.add(user)
	db.session.commit()



	# session = User.query.filter_by(id=request.json['sessionId']).first()


	# extract the token and granted scopes



	# requests.get('https://api.github.com/events',params=payload)
	# requests.post('https://httpbin.org/post',params=payload,data={'key':'value'})










@app.route("/files")
def files():
	session = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if session == None: return
	book = TemFile.query.filter_by(session_id = int(session.id),path=str(request.json['path'])).first()
	if book == None:
		r = requests.get("https://api.github.com/repos/"+session.owner+"/"+session.repo+"/contents/"+request.json['path']+"?ref="+session.branch)
		if r.status_code != 200:
			print(r.content)
			return
		con = r.json()
		book = TemFile(
			session_id = session.id,
			path = request.json['path'],
			content = con['content'],
			sha = con['sha']
		)
		db.session.add(book)
		db.session.commit()
	return book.content




@socketio.on('edit')
def handle_edit(edit):
	session = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if session == None: return
	book = TemFile.query.filter_by(session_id = int(session.id),path=str(request.json['path'])).first()
	if book == None: return
	book.content = book.content[:edit.delta.amt]+edit.delta.msg+book.content[edit.delta.amt:]
	db.session.commit()
	emit('edit',edit,include_self=False)


	

@app.route("/directories")
def directories():
	session = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if session == None: return
	r = requests.get("https://api.github.com/repos/"+session.owner+"/"+session.repo+"/git/trees/"+session.sha+"?recursive=1,ref="+session.branch)
	if r.status_code != 200:
		print(r.content)
		return
	return r.json()


@socketio.on('join')
def on_join(data):
	repo = Session.query.filter_by(owner=str(data['owner']),repo=str(data['repo'])).first()
	if repo == None: return

	sesh = Session.query.filter_by(project_id=int(repo.id)).first()
	if sesh == None:
		master = requests.get("https://api.github.com/repos/"+session.owner+"/"+session.repo+"/branches/master",headers={'Authorization':'token '+github_token})
		head_tree_sha = master.json()['commit']['commit']['tree']['sha']
		sesh = Session(
			owner      = repo.owner,
			repo       = repo.repo,
			branch     = repo.branch,
			sha        = head_tree_sha,
			project_id = repo.id,
			activemembers = str(request.sid)
		)
		db.session.add(sesh)
	else:
		sesh.activemembers = sesh.activemembers+","+str(request.sid)
	db.session.commit()

	join_room(str(repo.id)+","+str(sesh.id))
	emit('accept',{'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':request.sid},room=str(repo.id)+","+str(sesh.id),include_self=False)



@socketio.on('disconnect')
def on_disconnect():
	for sesh in Session.query:
		jj = sesh.activemembers.split(",")
		if request.sid in jj:
			jj.remove(request.sid)
		sesh.activemembers = ",".join(jj)
	db.session.commit()
	emit('player_leave',{'name':request.sid},include_self=False)











# @app.route("/projects",methods=['GET','POST'])
# @app.route("/projects/<int:id>",methods=['GET','PUT','DELETE'])


# @app.route("/projects/<int:id>/requests",methods=['GET','POST'])
# @app.route("/projects/<int:id>/requests/<int:rid>",methods=['DELETE'])



# @socketio.on('edit')
# def handle_my_custom_event(json):





# def getfiles():
# 	response = requests.get("http://127.0.0.1:5000")






if __name__ == '__main__':
    socketio.run(app,debug=True)



