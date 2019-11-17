from flask import render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import emit, join_room
from flask_dance.contrib.github import github
# from flask_session import Session
from app_factory import db, app, socketio
from models import Project, Session, TemFile
import base64
import requests
import json
import hashlib
import pprint
import copy



#as a side note, here are the basic patterns for notifying clients through socketio:
#room=request.sid        <---- notifies only the person that sent the message
#broadcast=True                      <---- (when inside a socketio route) notifies everyone connected to the session
#broadcast=True,include_self=False   <---- (when inside a socketio route) notifies everyone connected to the session except for the person initiating the event
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


@app.route('/favicon.ico')
def send_js():
    return send_from_directory('static/icons', 'favicon.ico')


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
	return redirect("/")


@app.route("/logout")
def logout():
	return "no you cant"


@socketio.on('connect')
def sdahoufa():
	print("user ", session['githubuser'], " connected")
	pass


@app.route("/files",methods=['POST'])
def files():
	return loadFile(request.json)

def loadFile(request):
	# request = {sessionId :"", path : ""}
	json_from_client = request
	sesh = Session.query.filter_by(id=int(json_from_client['sessionId'])).first()
	if sesh == None: return

	#creds=session['githubuser']
	#if creds not in sesh.activemembers.split(',') then tell the user to go directly to hell- dont give them any files they arent to be trusted.
	# if creds not in sesh.activemembers.split(','): return "ur not allowed lol",402

	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(json_from_client['path'])).first()
	if not book.loaded:
		
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
		book.content = decoded
		book.md5	 = hashlib.md5(decoded.encode("utf-8")).hexdigest()
		book.load()
		db.session.commit()
	return book.content



@socketio.on('edit')
def handle_edit(edit):
	sesh = Session.query.filter_by(id=int(edit['sessionId'])).first()
	if sesh == None: return
	book = TemFile.query.filter_by(session_id = int(sesh.id),path=str(edit['path'])).first()
	if book == None: return
	# print(edit)
	#synchronize.js line 237 is where this data comes from.

	#if creds not in sesh.activemembers.split(',') then automatically reject their change- they arent in the session.
	
	# if (creds not in sesh.activemembers.split(',')): 
	# 	emit('rejected',{"delta":edit['delta'],"reason":"invalid credentials"},room=request.sid) 
	# 	return
	hash = edit['md5']
	if(not book.addHash(hash, edit['delta'])): 
		emit('rejected',{"delta":edit['delta'],"mostRecentHash":book.hash1,"yourHash":hash},room=request.sid) 
		return
	# print("added hash: " , hash)
	book.change()
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


def git_commit(data, github_oauth_object):
	# data = {sessionId: "", commit_message : ""}, github_oauth
	# request.json() = [sessionId : "" , commit_message : ""]
	# github.put(url = url, params = par_var)
	# https://developer.github.com/v3/repos/contents/#create-or-update-a-file
	# https://developer.github.com/v3/git/
	# https://developer.github.com/v3/git/trees/
	access_token = github_oauth_object['access_token']
	print(github_oauth_object)
	print(access_token)
	headers = {"Authorization" : "token " + str(access_token)}
	sesh = Session.query.filter_by(id = data['sessionId']).first()
	commits = requests.get(url = "https://api.github.com/repos/" + sesh.owner + "/" + sesh.repo + "/commits",headers = headers)
	commits = commits.json()
	last_commit_sha = commits[0]['sha']
	commit_json_from_github = requests.get(url = "https://api.github.com/repos/" + sesh.owner + "/" + sesh.repo + "/commits/" + last_commit_sha, headers= headers)
	commit_json_from_github = commit_json_from_github.json()
	# formattedprint(commit_json_from_github)
	commit_tree_sha = commit_json_from_github['commit']['tree']['sha']
	github_tree = requests.get(url = "https://api.github.com/repos/"+sesh.owner+"/"+sesh.repo+"/git/trees/"+commit_tree_sha+"?recursive=1,ref="+sesh.branch,headers = headers)
	github_tree = github_tree.json()

	params = {
		"base_tree" : commit_tree_sha,
		"tree" : []
	}
	
	for file in TemFile.query.filter_by(session_id = int(data['sessionId'])).all():
		if (file.deleted):
			params["tree"].append({ "path" : file.path, "mode" : "100644", "type" : "blob", "sha" : None})
		else:
			params["tree"].append({ "path" : file.path, "mode" : "100644", "type" : "blob", "content" : file.content})

		# file == {id, session_id, path, content, sha, hash1-hash5}

	# https://developer.github.com/v3/git/trees/#create-a-tree
	
	# dict_keys(['_permanent', 'github_oauth_token', 'githubuser', 'sessionId'])
	# formattedprint(session.keys())
	# formattedprint(session['github_oauth_token'])
	# tree = params['tree']
	# formattedprint(github.get("/user").json())
	post_response = requests.post(url = "https://api.github.com/repos/" + sesh.owner + "/" + sesh.repo + "/git/trees", headers = headers , json= params)

	# print("\n"*10)
	# formattedprint(requests.post('http://httpbin.org/post', json = params).json())
	# print("\n"*10)
	# https://developer.github.com/v3/git/trees/#response-2
	# formattedprint("post response: " , post_response.json())
	# formattedprint("post response: " , post_response.status_code)
	post_response = post_response.json()
	
	# out of for loop

	# todo: commit
	new_tree_sha = post_response['sha']
	commit_data = {
	 "message" : str(data['commit_message']),
	 "parents" : [str(last_commit_sha)],
	 "tree" : str(new_tree_sha)
	}


	# POST /repos/:owner/:repo/git/commits
	# https://developer.github.com/v3/git/commits/#create-a-commit
	git_commit_json = requests.post(url = "https://api.github.com/repos/" + sesh.owner + "/" + sesh.repo + "/git/commits", headers = headers, json = commit_data).json()
	# print("\n\nMake a new commit object response: ", git_commit_json)
	sha = git_commit_json['sha']
	if (git_commit_json['verification']['verified'] == False):
		print("Commit unverified")
		print("Reason: ", git_commit_json["verification"]['reason'])


	# todo: update the branch to point to the commit sha
	# https://developer.github.com/v3/git/refs/#get-a-single-reference
	print("Committing....")
	if (requests.get(url = "https://api.github.com/repos/" + sesh.owner + "/" + sesh.repo + "/git/ref/heads/" + sesh.branch,headers = headers).status_code == 404):
		# make a new branch if the branch doesn't exist
		# test this 
		# either post or patch, idk man
		# POST /repos/:owner/:repo/git/refs
		# PATCH /repos/:owner/:repo/git/refs/:ref
		# POST :::: Create a branch
		# PATCH ::: Update a branch
		print("Branch " + str(sesh.branch) + " not found, committing to branch 'synergi'")
		if(requests.get( url = "https://api.github.com/repos/" + sesh.owner + "/"+ sesh.repo +"/git/refs/heads/synergi",headers = headers).status_code == 404):
			print("Branch synergi not found, making synergi then committing to branch synergi")
			requests.post( url = "https://api.github.com/repos/" + sesh.owner + "/"+ sesh.repo +"/git/refs/heads/synergi", headers = headers, json = {"ref" : "refs/heads/synergi", "sha" : sha})
		else:
			print("Committing to branch synergi")
			requests.patch( url = "https://api.github.com/repos/" + sesh.owner + "/"+ sesh.repo +"/git/refs/heads/synergi", headers = headers, json = {"sha" : sha, "force" : False})
	else:
		response = requests.post( url = "https://api.github.com/repos/" + sesh.owner + "/"+ sesh.repo +"/git/refs/heads/" + sesh.branch, headers = headers, json = {"ref" : "refs/heads/" + sesh.branch, "sha" : sha}).json()
		print("pointing commit to branch response: ", response)

	print("Commit successful")
@app.route("/commit", methods = ["POST"])
def commit():
	data = request.json
	git_commit(data, session['github_oauth_token'])
	




@socketio.on('deletefile')
def filedelete(data):
	#input:
		#data['sessionId']
		#data['path']      #the place the file is
		#data['directory'] #true if the file in question is a directory. False if the file is not a directory.
	#output:
		#if you can't find the file, the call is invalid and you should emit suspect_desynchronization to the user. (don't broadcast)
		#emit deletefile to everyone (including the user/include_self) if the call is valid

	#considerations:
		#you need to worry about the case where the user tries to delete a directory full of files.
			#directories contain other files, so when they are moved, many files end up being deleted at once.
			#the server needs to delete everything contained inside the folder if a folder is deleted.
	if data['path'] == None:
		emit("suspect_desynchronization")

	if not data['directory']:
		file = TemFile.query.filter_by(session_id=data['sessionId'], path=data['path']).first()
		if (file == None):
			emit("suspect_desynchronization")
			return
		file.delete()
	else:
		file_tree = TemFile.query.filter_by(session_id = data['sessionId']).all()
		files = [each for each in file_tree if each.path.startswith(data['path'] + "/")]
		for f in files:
			f.delete()

	db.session.commit()
	emit("deletefile", data, broadcast = True, include_self = True)
	


@socketio.on('fileupdate')
def fileupdate(data):
	#input:
		#data['sessionId']
		#data['oldpath']   #the place the file used to be. This is None if the user is creating a file.
		#data['newpath']   #the place the file ought to be.
		#data['directory'] #true if the file in question is a directory. False if the file is not a directory.
	#output:
		#if they supply either a source or destination path that ends in a /, the call is invalid.
		#if they supply a source path and but you can't find the file to move, the call is invalid.
		#if a file already exists at the destination path, the call is invalid.
		#if the user inputs an invalid destination path, the call is invalid.
		#if the call is invalid, emit suspect_desynchronization to that client (don't broadcast it to everyone)
		#if the call is valid, emit fileupdate with the same data to all the other clients (broadcast and do not include self)

	#considerations:
		#you need to worry about the case where the user tries to move a directory from one spot to another.
			#directories contain other files, so when they are moved, many files end up being moved at once.
			#the server needs to update the paths of every file/directory moved, which may be more than one if the user moves a folder.
		#make sure the destination path is valid i.e. it's located inside a directory and it's written with characters that are allowed to appear in the path.
	
	# if there is a file at the specified new path, start pooping on the keyboard and return an error
	if data['newpath']== "" or data['newpath'][-1]=="/":
		emit("suspect_desynchronization")
		return
	tmp = TemFile.query.filter_by(path = data['newpath']).first()
	if tmp != None:
		if not tmp.deleted:
			emit("suspect_desynchronization")
			return
		db.session.delete(tmp)
		db.session.commit()


	if data['oldpath'] == None:
		if data['directory']:
			file = TemFile(
					session_id = data['sessionId'],
					path = data['newpath'],
					content = "",
					sha = None,
					md5 = hashlib.md5("".encode("utf-8")).hexdigest()
				)
			db.session.add(file)
			db.session.commit()
			print("Created file")
		else:
			pass
		emit("fileupdate", data, broadcast=True,include_self=False)
		return

	file = TemFile.query.filter_by(session_id = data['sessionId'], path = data['oldpath']).first()
	if file == None: # if the file does not exist, somethin wonky is happening
		emit("suspect_desynchronization")
		return

	# File move
	if not data['directory']:
		atomicMoveFile(file, data['newpath'])
		db.session.commit()

	# TODO: make folder move
	else:
		file_tree = TemFile.query.filter_by(session_id = data['sessionId']).all()
		files = [each for each in file_tree if each.path.startswith(data['oldpath'] + "/")]
		for file in files:
			atomicMoveFile(file, data['newpath'] + "/" + file.path[len(data['oldpath'])+1:])
		db.session.commit()



	emit("fileupdate", data, broadcast=True,include_self=False)
	

# make the file move update the path and create a new temfile with no content, the old path, and property of deleted

def atomicMoveFile(file, newpath):
	junkFile = TemFile(
		session_id = file.session_id,
		path = file.path,
		content = "",
		sha = file.sha,
		md5 = file.md5
	)
	junkFile.delete()
	db.session.add(junkFile)
	file.path = newpath


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
		print("session does not exist, creating new session")
		master = github.get("/repos/"+repo.owner+"/"+repo.repo+"/branches/"+repo.branch)
		head_tree_sha = master.json()['commit']['commit']['tree']['sha']
		sesh = Session(
			owner      = repo.owner,
			repo       = repo.repo,
			branch     = repo.branch,
			sha        = head_tree_sha,
			project_id = repo.id,
			activemembers = None,
		)
		db.session.add(sesh)
		db.session.commit()
		# make every file in the tree a temFile

		file_tree = github.get("/repos/"+ repo.owner +"/"+ repo.repo +"/git/trees/"+ head_tree_sha +"?recursive=1")
		for file in file_tree['tree']:
			book = TemFile(
				session_id = sesh.id,
				path = file['path'],
				content = "",
				sha = file['sha'],
				md5 = hashlib.md5("".encode("utf-8")).hexdigest()
			)
			db.session.add(book)
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
	
	print()
	members_array = sesh.activemembers
	if sesh.activemembers == None: members_array = []
	print("current members:: ", members_array)
	print("user " , creds , " joining session")
	
	if creds in members_array:
		print("member in session already")


	members_array.append(creds)
	sesh.activemembers = members_array
	print("\nUsers:")
	for item in sesh.activemembers:
		print(item)

	
	db.session.commit()
	print("user ", members_array[len(members_array)-1], " joined")

	join_room("room:"+str(sesh.id))

	session['sessionId'] = sesh.id
	
	emit('accept',{'project':repo.serialize(),'sessionId':sesh.id,'activemembers':sesh.activemembers},room=request.sid)
	emit('player_join',{'name':creds},broadcast=True,include_self=False)


@socketio.on('disconnect')
def on_disconnect():
	data = request.json()
	creds = session['githubuser']
	print("disconnecting....")
	sesh = Session.query.filter_by(id = session['sessionId']).first()
	print("current users: ", sesh.activemembers)
	members_array = sesh.activemembers
	members_array = copy.copy(members_array)
	if creds in members_array: members_array.remove(creds)
	sesh.activemembers = members_array
	print("temp: ", sesh.activemembers)
	db.session.commit()
	print("Active users: ", sesh.activemembers)
	if (sesh.activemembers == []):
		print("Session empty")
		print("Auto-committing")
		git_commit({"sessionId" : session['sessionId'], "commit_message": "Auto-generated Commit"}, session["github_oauth_token"])
		for sesh in Session.query.filter_by(project_id = data["projectid"]).all():
		#in the future we'd have to emergency push all data in each session before a session gets deleted. This applies here and also when people disconnect from sessions.
			TemFile.query.filter_by(session_id = sesh.id).delete()
		Session.query.filter_by(project_id = data["projectid"]).delete()
	emit('player_leave',{'name':creds},include_self=False)


if __name__ == '__main__':
	socketio.run(app,debug=True,keyfile='key.pem', certfile='cert.pem')






