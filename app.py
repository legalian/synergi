from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
import requests
# from flask.ext.heroku import Heroku
import os
# import eventlet
# eventlet.monkey_patch()


# from flask_dance.consumer.storage import BaseStorage



app = Flask(__name__)
socketio = SocketIO(app)
# heroku = Heroku(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Session(app)

from models import Project, Session, TemFile


blueprint = make_github_blueprint(
    client_id=os.environ['GITHUB_CLIENT_ID'],
    client_secret=os.environ['GITHUB_CLIENT_SECRET'],
)
app.register_blueprint(blueprint, url_prefix="/login")



def gitcreds(github):
	if not github.authorized: return None
	print("sidjfoisdf")
	resp = github.get("/user").json()["login"]
	session['githubuser'] = resp
	print(session.get('github_oauth'))
	# session['github'] = github
	print("oiwjfeoiwjef")
	return resp



@app.route('/template')
def frickyouParker():
	return render_template('/template.html')


@app.route("/")
def index():
	return render_template('index.html',creds=gitcreds(github))

@app.route("/projectlist")
def projectlist():
	return render_template('todolist.html',creds=gitcreds(github))



@app.route("/repos")
def repos():
	openrepos = []
	res = []
	for i in github.get("/user/repos").json():
		print("accessing:"+str(i['owner']['login'])+","+str(i['name']))
		print([k.serialize() for k in Project.query.all()])


		repo = Project.query.filter_by(owner=str(i['owner']['login']),repo=str(i['name'])).first()
		if repo != None:
			res.append(repo.serialize())

		openrepos.append({
			'owner':str(i['owner']['login']),
			'name':str(i['name']),
			'branches':[p['name'] for p in github.get("/repos/"+str(i['owner']['login'])+"/"+str(i['name'])+"/branches").json()]
		})
	return {'openrepos':openrepos,'res':res}



@app.route("/projects",methods=['POST'])
def projects():
	yam = request.form
	proj = Project(
		name       = str(yam['name']),
		repo       = str(yam['repo']),
		branch     = str(yam['branch']),
		owner      = str(yam['owner']),
		description = str(yam['description'])
	)
	db.session.add(proj)
	db.session.commit()
	return projectlist();



# @app.route("/projects/<int:id>",methods=['GET','PUT','DELETE'])
# def project(id):
# 	if request.method == 'GET':






@app.route("/editor")
def editor():
	return render_template('editor.html',creds=gitcreds(github))



@app.route("/gitlogin")
def login():
	if not github.authorized:
		return redirect(url_for("github.login"))
	resp = github.get("/user")
	return redirect("/")

# @app.route("/login")
# def login():
#     if not github.authorized:
#         return redirect(url_for("github.login"))
#     resp = github.get("/user")
#     return redirect("/")
#     # assert resp.ok
#     # print(resp.json())
#     # return "You are @{login} on GitHub".format(login=resp.json()["login"])




@app.route("/logout")
def logout():
	return "jw9ejfoweufj"




@socketio.on('connect')
def sdahoufa():
	print("fuck you");
	print("fuck you");
	print("fuck you");
	print("fuck you");
	print("fuck you");





@app.route("/files")
def files():
	jak = request.json()
	sesh = Session.query.filter_by(id=int(jak['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(jak['path'])).first()
	if book == None:
		r = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/contents/"+jak['path']+"?ref="+sesh.branch)
		if r.status_code != 200:
			print(r.content)
			return
		con = r.json()
		book = TemFile(
			session_id = sesh.id,
			path = jak['path'],
			content = con['content'],
			sha = con['sha']
		)
		db.session.add(book)
		db.session.commit()
	return book.content




@socketio.on('edit')
def handle_edit(edit):
	sesh = Session.query.filter_by(id=int(edit['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(edit['path'])).first()
	if book == None: return
	book.content = book.content[:edit.delta.amt]+edit.delta.msg+book.content[edit.delta.amt:]
	db.session.commit()
	emit('edit',edit,include_self=False)


	

@app.route("/directories")
def directories():
	sesh = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if sesh == None: return
	r = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/git/trees/"+sesh.sha+"?recursive=1,ref="+sesh.branch)
	if r.status_code != 200:
		print(r.content)
		return
	return r.json()


@socketio.on('join')
def on_join(data):
	print("JOIN GOT")
	repo = Project.query.filter_by(id=int(data['projectId'])).first()
	print("REPO GOT")
	if repo == None: return
	creds=session['githubuser']
	print("CREDS GOT")
	if creds == None: return

	sesh = Session.query.filter_by(project_id=int(repo.id)).first()
	print("SESSION GOT")
	if sesh == None:
		master = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/branches/"+sesh.branch)
		head_tree_sha = master.json()['commit']['commit']['tree']['sha']
		print("COMMIT GOT")
		sesh = Session(
			owner      = repo.owner,
			repo       = repo.repo,
			branch     = repo.branch,
			sha        = head_tree_sha,
			project_id = repo.id,
			activemembers = creds
		)
		db.session.add(sesh)
		print("SESSION ADD")
	else:
		print("COMMIT EXISTS")
		sesh.activemembers = sesh.activemembers+","+creds
	print("PRECOMMIT")
	db.session.commit()
	print("POSTCOMMIT")


	join_room(str(repo.id)+","+str(sesh.id))
	emit('accept',{'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':creds},room=str(repo.id)+","+str(sesh.id),include_self=False)


	print("fuck asdfjanskdfyou");
	print("fuck kyou");
	print("fuck ydjfnjdfnou");
	print("fuck jdnfjndjfyou");



@socketio.on('disconnect')
def on_disconnect():
	for sesh in Session.query:
		jj = sesh.activemembers.split(",")
		if request.sid in jj:
			jj.remove(request.sid)
		sesh.activemembers = ",".join(jj)
	db.session.commit()
	creds=session['githubuser']
	emit('player_leave',{'name':creds},include_self=False)











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



