from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
import base64
import requests
import os
import hashlib
import sys
import platform
from subprocess import Popen

# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# from werkzeug.exceptions import HTTPException

# log = logging.getLogger('eventlet')
# log.setLevel(logging.ERROR)



from app_factory import db,app,blueprint,socketio
# from flask_dance.consumer.storage import BaseStorage

from models import Project, Session, TemFile

app.config['ssl_verify_client_cert'] = True
app.logger.disabled = True




def print(*args):
	sample = open('log.txt', 'a') 
	sample.write(' '.join([repr(k) if type(k) is not str else k for k in args])+'\n')
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
		#in the future we'd have to emergency push all data in each session before a session gets deleted. This applies here and also when people disconnect from sessions.
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
	return redirect("/projectlist")


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

	#creds=session['githubuser']
	#if creds not in sesh.activemembers.split(',') then tell the user to go directly to hell- dont give them any files they arent to be trusted.


	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(jak['path'])).first()
	print(book)
	if book == None:
		#I'd need to look more into the github api, but i think github does something special when the files are too large to be sent over their api or smth
		#maybe we can set our own filesize limits or we have two separate aborts, one for when its so large that it breaks the api, and one when its not quite that large but we still won't keep it in our database.
			#either way we just return 413
		if False:
			return "Content too large",413#pretty sure this sends back a 413 error code, which I can interpret on front end.
		r = github.get("/repos/"+sesh.owner+"/"+sesh.repo+"/contents/"+jak['path']+"?ref="+sesh.branch)
		if r.status_code != 200:
			print(r.content)
			return

		#you'll need to calculate the md5 hash here as well, for the new TemFile object youre creating
		con = json.loads(r.content)
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
	creds=session['githubuser']
	sesh = Session.query.filter_by(id=int(edit['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(edit['path'])).first()
	if book == None: return
	print(edit)
	#synchronize.js line 237 is where this data comes from.

	#if creds not in sesh.activemembers.split(',') then automatically reject their change- they arent in the session.

	#edit['md5'] would be the hash that comes from the client. You compare this hash against the server's hashes.
	#no matching hash found: reject change
	#after you apply the change, the server calculates the md5 of the new data (for security reasons you cant rely on the client to calculate both hashes)
	#new hash becomes current version, old hash gets added to the list along with the delta and stored in the database.
		#to add columns to the database, which you will need to do for this step, first modify models.py and then run:
			#python manage.py db migrate
			#python manage.py db upgrade
		#TemFile is the table youd want to add the versioning stuff to.

	#for change in changes_between_matching_hash_and_current_hash:
		#if change overlaps current_delta: reject change and exit
		#if change comes before current_delta: current_delta.start+=len(change.data)-change.amt

	if False:#this is what you do when you reject a change
		emit('rejected',{delta:edit['delta']},room=request.sid)
		#as a side note, here are the basic patterns for notifying clients through socketio:
		#room=request.sid        <---- notifies only the person that sent the message
		#broadcast=True                      <---- (when inside a socketio route) notifies everyone connected to the session
		#broadcast=True,include_self=False   <---- (when inside a socketio route) notifies everyone connected to the session except for the person initiating the event
		#room=str(repo.id)+","+str(sesh.id)                      <----(when inside a flask route) notifies everyone connected to the session
		#room=str(repo.id)+","+str(sesh.id),include_self=False   <----(when inside a flask route) notifies everyone connected to the session except for the person initiating the event
		#clients recieve these events with shit like: socket.on('rejected',function(data){console.log(data);})



	book.content = book.content[:edit['delta']['start']]+edit['delta']['msg']+book.content[edit['delta']['start']+edit['delta']['amt']:]


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

	#github api calls are done with github.get(path) or github.post(path). you can see the pattern below.
	#here we need to tell the user to fuck themselves with a rusty pipe if they try to edit a repo they dont have write permissions for
	#dunno which api endpoint to hit but its probably not too bad


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

	#not sure how youd go about verifying that a user has write permissions here... i may have written myself into a corner...

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


# my_logger = logging.getLogger('my-logger')
# my_logger.setLevel(logging.ERROR)

# messages = 'This is Console1', 'This is Console2'

# # define a command that starts new terminal
# if platform.system() == "Windows":
#     new_window_command = "cmd.exe /c start".split()
# else:  #XXX this can be made more portable
#     new_window_command = "x-terminal-emulator -e".split()

# # open new consoles, display messages
# echo = [sys.executable, "-c",
#         "import sys; print(sys.argv[1]); input('Press Enter..')"]
# processes = [Popen(new_window_command + echo + [msg])  for msg in messages]





if __name__ == '__main__':
	# ssl_verify_client_cert = True
	# context = ('local.crt', 'local.key')#certificate and key files. 
	# subprocess.call(["tail -f log.txt"]) 

	# subprocess.Popen('ls',stdout=subprocess.PIPE)


	socketio.run(app,debug=True,keyfile='key.pem', certfile='cert.pem')#ssl-enable3
	#eventlet.monkey_patch(socket=False)






