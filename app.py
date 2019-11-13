from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
from app_factory import db,app,blueprint,socketio
from models import Project, Session, TemFile
import base64
import requests
import os
import json
import hashlib
import sys
import json
import pprint


#as a side note, here are the basic patterns for notifying clients through socketio:
#room=request.sid        <---- notifies only the person that sent the message
#broadcast=True                      <---- (when inside a socketio route) notifies everyone connected to the session
#broadcast=True,include_self=False   <---- (when inside a socketio route) notifies everyone connected to the session except for the person initiating the event
#room=str(repo.id)+","+str(sesh.id)                      <----(when inside a flask route) notifies everyone connected to the session
#room=str(repo.id)+","+str(sesh.id),include_self=False   <----(when inside a flask route) notifies everyone connected to the session except for the person initiating the event
#clients recieve these events with shit like: socket.on('rejected',function(data){console.log(data);})



app.config['ssl_verify_client_cert'] = True
app.logger.disabled = True

def print(*args):
	sample = open('log.txt', 'a') 
	sample.write(' '.join([repr(k) if type(k) is not str else k for k in args])+'\n')
	sample.close()

def formattedprint(*args):
	sample = open('log.txt', 'a') 
	sample.write(' '.join([pprint.pformat(k,compact=True) if type(k) is not str else k for k in args])+'\n')
	sample.close()

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
	print("oasdjfoaisdjfoiajsdf")
	return render_template('index.html',creds=gitcreds(github))

@app.route("/projectlist")
def projectlist():
	if not github.authorized:
		return redirect(url_for("github.login"))
	return render_template('todolist.html',creds=gitcreds(github))



@app.route("/github_repos")
def github_repos():
	openrepos = []

	# github.get("/user/repos")
	# https://developer.github.com/v3/repos/#list-your-repositories
	for i in github.get("/user/repos").json():
		# TODO: only add if they are a collaborator 
		# https://developer.github.com/v3/repos/collaborators/#list-collaborators

		# print(github.get("/repos/"+str(i['owner']['login'])+"/"+str(i['name'])+"/branches").json())

		openrepos.append({
			'owner':str(i['owner']['login']),
			'name':str(i['name']),
			'branches':[p['name'] for p in github.get("/repos/"+str(i['owner']['login'])+"/"+str(i['name'])+"/branches").json()]
		})
	return {"payload": openrepos}

@app.route("/synergi_repos")
def synergi_repos():
	results = []
	#load client repos from database
	user = "{"+session['githubuser']+"}"
	# Project.query.filter_by(owner=str(i['owner']['login']),repo=str(i['name'])).all()
	for repo in Project.query.filter(Project.write_access_users.contains(user)).all():
		results.append(repo.serialize())

	return {"payload":results}






@app.route("/deleteObject", methods=['POST'])
def deleteObject():
	data = request.json

	for sesh in Session.query.filter_by(project_id = data["projectid"]).all():
		#in the future we'd have to emergency push all data in each session before a session gets deleted. This applies here and also when people disconnect from sessions.
		TemFile.query.filter_by(session_id = sesh.id).delete()
	Session.query.filter_by(project_id = data["projectid"]).delete()
	Project.query.filter_by(id = data["projectid"]).delete()
	
	db.session.commit()
	return "200"


@app.route("/projects",methods=['POST'])
def projects():
	json_from_client = request.json
	# formattedprint("/repos/" + str(json_from_client['owner']) + "/" + str(json_from_client['repo']) + "/contributors")
	# print("-=-=-=->",json_from_client)


	users = github.get("/repos/" + str(json_from_client['owner']) + "/" + str(json_from_client['repo']) + "/contributors").json()
	# formattedprint(users)

	write_user_list = []
	for user in users:
		write_user_list.append(user['login'])

	proj = Project(
		name       = str(json_from_client['name']),
		repo       = str(json_from_client['repo']),
		branch     = str(json_from_client['branch']),
		owner      = str(json_from_client['owner']),
		description = str(json_from_client['description']),
		write_access_users = write_user_list
	)
	db.session.add(proj)
	db.session.commit()
	print("osdijfaosijdfoaisjdfoaisjdfoiasjdf\n\n\n\n")
	return {"projectId":proj.id}

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
	json_from_client = request.json
	sesh = Session.query.filter_by(id=int(json_from_client['sessionId'])).first()
	if sesh == None: return

	#creds=session['githubuser']
	#if creds not in sesh.activemembers.split(',') then tell the user to go directly to hell- dont give them any files they arent to be trusted.
	creds = session['githubuser']
	# if creds not in sesh.activemembers.split(','): return "ur not allowed lol",402

	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(json_from_client['path'])).first()
	print(book)
	if book == None:
		
		# pulls the information of the file from github 
		# https://developer.github.com/v3/repos/contents/
		github_request = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/contents/"+json_from_client['path']+"?ref="+sesh.branch)
		if github_request.status_code != 200:
			print(github_request.content)
			return

		json_from_github = json.loads(github_request.content)

		# checks to see if the files are above 256KB, and if they are, return error code 413
		if json_from_github['size'] > 262144 :
			return "Content too large",413
		
		decoded = str(base64.b64decode(json_from_github['content']).decode("utf-8"))

		# making the database entry in TemFile of the current file
		book = TemFile(
			session_id = sesh.id,
			path = json_from_client['path'],
			content = decoded,
			sha = json_from_github['sha'],
			md5 = hashlib.md5(decoded.encode("utf-8")).hexdigest()
		)

		db.session.add(book)
		db.session.commit()
	return book.content



@socketio.on('edit')
def handle_edit(edit):
	creds=session['githubuser']
	sesh = Session.query.filter_by(id=int(edit['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(edit['path'])).first()
	if book == None: return
	print(edit)
	#synchronize.js line 237 is where this data comes from.

	#if creds not in sesh.activemembers.split(',') then automatically reject their change- they arent in the session.
	
	# if (creds not in sesh.activemembers.split(',')): 
	# 	emit('rejected',{"delta":edit['delta'],"reason":"invalid credentials"},room=request.sid) 
	# 	return
	
	hash = edit['md5']
	if(not book.addHash(hash, edit['delta'])): 
		emit('rejected',{"delta":edit['delta'],"mostRecentHash":book.hash1,"yourHash":hash},room=request.sid) 
		return
	print("added hash: " , hash)
	db.session.commit()
	emit('edit',edit,broadcast=True,include_self=False)


	

@app.route("/directories",methods=['POST'])
def directories():
	sesh = Session.query.filter_by(id=int(request.json['sessionId'])).first()
	if sesh == None: return
	github_request = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/git/trees/"+sesh.sha+"?recursive=1,ref="+sesh.branch)
	if github_request.status_code != 200: return
	json_github_request = github_request.json()

	# https://developer.github.com/v3/git/trees/#get-a-tree
	if len(json_github_request['tree']) > 1000 or json_github_request['truncated']:
		return "too many files", 413
	return json_github_request


# do a double check the user has write permissions; query github to check 
# https://developer.github.com/v3/repos/#list-user-repositories
# or 
# given repo output collaborators 
@app.route("/join", methods=['POST'])
def joinjoin():
	data = request.json
	repo = Project.query.filter_by(id=int(data['projectId'])).first()
	if repo == None: return "nah bruh",403
	creds=session['githubuser']
	if creds == None: return "nah son- you got no credentials",403

	#github api calls are done with github.get(path) or github.post(path). you can see the pattern below.
	#here we need to tell the user to fuck themselves with a rusty pipe if they try to edit a repo they dont have write permissions for
	#dunno which api endpoint to hit but its probably not too bad

	write_user_list = github.get("/repos/"+repo.owner+"/"+repo.repo + "/contributors").json()
	for user in write_user_list:
		if user['login'] == session['githubuser']:
			break
	else:
		return "User does not have write access", 403


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
			activemembers = "",
		)
		db.session.add(sesh)
		db.session.commit()


	session['sessionId'] = sesh.id

	return "OK"


@socketio.on('join')
def on_join(data):
	repo = Project.query.filter_by(id=int(data['projectId'])).first()
	if repo == None: return
	creds = session['githubuser']
	if creds == None: return

	for user in repo.write_access_users:
		if user == session['githubuser']:
			break
	else:
		return "User does not have write access", 403

	sesh = Session.query.filter_by(project_id=int(repo.id)).first()
	if sesh == None: return
	members = sesh.activemembers
	members_array = [] if members == "" else members.split(",")
	if creds not in members_array:
		members_array.append(creds)
		sesh.activemembers = ",".join(members_array)
		db.session.commit()

	join_room(str(repo.id)+","+str(sesh.id))
	emit('accept',{'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':creds},room=str(repo.id)+","+str(sesh.id),include_self=False)


@socketio.on('disconnect')
def on_disconnect():
	creds = session['githubuser']
	for sesh in Session.query.filter_by(id=int(session['sessionId'])).all():
		members_array = sesh.activemembers.split(",")
		if creds in members_array:
			print("\n\n\nfound ", members_array, creds )
			members_array.remove(creds)
			print("\n\n\nremoved ", members_array, creds)
		else:
			print("\n\n\nnot found: ", members_array, creds )
		sesh.activemembers = ",".join(members_array)
	db.session.commit()
	emit('player_leave',{'name':creds},include_self=False)


if __name__ == '__main__':
	socketio.run(app,debug=True,keyfile='key.pem', certfile='cert.pem')






