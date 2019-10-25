from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
import base64
import requests
import os
import hashlib

from app_factory import db,app,blueprint,socketio
# from flask_dance.consumer.storage import BaseStorage

from models import Project, Session, TemFile

app.config['ssl_verify_client_cert'] = True

##################################
	
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
	resp = github.get("/user").json()["login"]
	session['githubuser'] = resp
	return resp


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

		for repo in Project.query.filter_by(owner=str(i['owner']['login']),repo=str(i['name'])).all():
			res.append(repo.serialize())

		openrepos.append({
			'owner':str(i['owner']['login']),
			'name':str(i['name']),
			'branches':[p['name'] for p in github.get("/repos/"+str(i['owner']['login'])+"/"+str(i['name'])+"/branches").json()]
		})
	return {'openrepos':openrepos,'res':res}

@app.route("/deleteObject", methods=['POST'])
def deleteObject():
	data = request.json

	for sesh in Session.query.filter_by(project_id = data["projectid"]).all():
		TemFile.query.filter_by(session_id = sesh.id).delete()
	Session.query.filter_by(project_id = data["projectid"]).delete()
	Project.query.filter_by(id = data["projectid"]).delete()



	db.session.commit()

	for yams in Project.query.filter_by(id = data["projectid"]).all():
		print(yams.serialize())
	else:
		print("Nothing to delete after")



	return "200"


@app.route("/projects",methods=['POST'])
def projects():
	yam = request.form
	print("OAIJDFOIAJDOIASJDOFIJSDFOIJSDLKFJSLKDFJLSKDFJLKSDJFLKSDFJLKSDFJ\n\n\n\n")
	proj = Project(
		name       = str(yam['name']),
		repo       = str(yam['repo']),
		branch     = str(yam['branch']),
		owner      = str(yam['owner']),
		description = str(yam['description'])
	)
	db.session.add(proj)
	db.session.commit()
	return "200"


@app.route("/editor")
def editor():
	return render_template('editor.html',creds=gitcreds(github))



@app.route("/gitlogin")
def login():
	if not github.authorized:
		return redirect(url_for("github.login"))
	resp = github.get("/user")
	return redirect("/")


@app.route("/logout")
def logout():
	return "no you cant"




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
		# con = r.json()
		con = json.loads(r.content)

		#json.loads(result.content)
		decoded = str(base64.b64decode(con['content']).decode("utf-8"))
		book = TemFile(
			session_id = sesh.id,
			path = jak['path'],
			content = decoded,
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
	print(edit)
	book.content = book.content[:edit['delta']['start']]+edit['delta']['msg']+book.content[edit['delta']['start']+edit['delta']['amt']:]

	# if edit['mode'] == 'insert':
	# 	book.content = book.content[:edit['delta']['amt']]+edit['delta']['msg']+book.content[edit['delta']['amt']:]
	# elif edit['mode'] == 'remove':
	# 	book.content = book.content[:edit['delta']['amt']]+book.content[edit['delta']['amt']+len(edit['delta']['msg']):]
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

	session['sessionId'] = sesh.id

	join_room(str(repo.id)+","+str(sesh.id))
	emit('accept',{'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':creds},room=str(repo.id)+","+str(sesh.id),include_self=False)




@socketio.on('disconnect')
def on_disconnect():
	creds=session['githubuser']
	for sesh in Session.query.filter_by(id=int(session['sessionId'])).all():
		jj = sesh.activemembers.split(",")
		if creds in jj:
			jj.remove(creds)
		sesh.activemembers = ",".join(jj)
	db.session.commit()
	emit('player_leave',{'name':creds},include_self=False)


if __name__ == '__main__':
	ssl_verify_client_cert = True
	# context = ('local.crt', 'local.key')#certificate and key files
	socketio.run(app,debug=True,keyfile='key.pem', certfile='cert.pem')
	#eventlet.monkey_patch(socket=False)
