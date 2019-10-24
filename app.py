from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
import base64
import requests
import os

from app_factory import db,app,blueprint,socketio
# from flask_dance.consumer.storage import BaseStorage

from models import Project, Session, TemFile

app.config['ssl_verify_client_cert'] = True

##################################
# app = Flask(__name__)

@app.route('/components')
def components():
	return render_template('test.html')

@app.route('/animation')
def animation():
	return render_template('animationeditor.html')

@app.route('/music')
def music():
	return render_template('grapheditor.html')


##################################


def gitcreds(github):
	if not github.authorized: return None
	# print("sidjfoisdf")
	resp = github.get("/user").json()["login"]
	session['githubuser'] = resp
	# print(session.get('github_oauth'))
	# session['github'] = github
	# print("oiwjfeoiwjef")
	return resp



@app.route('/template')
def frickyouParker():
	return render_template('/template.html')


@app.route("/")
def index():
	return render_template('index.html',creds=gitcreds(github))

@app.route("/projectlist")
def projectlist():
	if not github.authorized:
		return redirect(url_for("github.login"))
	return render_template('todolist.html',creds=gitcreds(github))



@app.route("/repos")
def repos():
	openrepos = []
	res = []
	for i in github.get("/user/repos").json():
		# print("accessing:"+str(i['owner']['login'])+","+str(i['name']))
		# print([k.serialize() for k in Project.query.all()])


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
	pass
	





@app.route("/files",methods=['POST'])
def files():
	jak = request.json
	sesh = Session.query.filter_by(id=int(jak['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(jak['path'])).first()
	print(book)
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
		# print("book added")
		db.session.add(book)
		db.session.commit()
	return book.content




@socketio.on('edit')
def handle_edit(edit):
	sesh = Session.query.filter_by(id=int(edit['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(edit['path'])).first()
	if book == None: return
	if edit['mode'] == 'insert':
		book.content = book.content[:edit['delta']['amt']]+edit['delta']['msg']+book.content[edit['delta']['amt']:]
	elif edit['mode'] == 'remove':
		book.content = book.content[:edit['delta']['amt']]+book.content[edit['delta']['amt']+len(edit['delta']['msg']):]
	db.session.commit()
	emit('edit',edit,broadcast=True,include_self=False)


	

@app.route("/directories",methods=['POST'])
def directories():
	# print(dict(request.json))
	sesh = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if sesh == None: return
	r = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/git/trees/"+sesh.sha+"?recursive=1,ref="+sesh.branch)
	if r.status_code != 200:
		print(r.content)
		return
	return r.json()



@app.route("/join", methods=['POST'])
def joinjoin():
	data = request.json
	repo = Project.query.filter_by(id=int(data['projectId'])).first()
	if repo == None: return
	creds=session['githubuser']
	if creds == None: return

	sesh = Session.query.filter_by(project_id=int(repo.id)).first()
	if sesh == None:
		master = github.get("/repos/"+repo.owner+"/"+repo.repo+"/branches/"+repo.branch)
		head_tree_sha = master.json()['commit']['commit']['tree']['sha']
		sesh = Session(
			owner      = repo.owner,
			repo       = repo.repo,
			branch     = repo.branch,
			sha        = head_tree_sha,
			project_id = repo.id,
			activemembers = ""
		)
		db.session.add(sesh)
		db.session.commit()
	return "OK"




@socketio.on('join')
def on_join(data):
	repo = Project.query.filter_by(id=int(data['projectId'])).first()
	if repo == None: return
	creds=session['githubuser']
	if creds == None: return

	sesh = Session.query.filter_by(project_id=int(repo.id)).first()
	if sesh == None: return
	sesh.activemembers = sesh.activemembers+","+creds
	db.session.commit()


	join_room(str(repo.id)+","+str(sesh.id))
	emit('accept',{'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':creds},room=str(repo.id)+","+str(sesh.id),include_self=False)




@socketio.on('disconnect')
def on_disconnect():
	creds=session['githubuser']
	for sesh in Session.query:
		jj = sesh.activemembers.split(",")
		if creds in jj:
			jj.remove(creds)
		sesh.activemembers = ",".join(jj)
	db.session.commit()
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
	ssl_verify_client_cert = True
	# context = ('local.crt', 'local.key')#certificate and key files
	socketio.run(app,debug=True,keyfile='key.pem', certfile='cert.pem')
	#eventlet.monkey_patch(socket=False)












