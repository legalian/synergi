from app import db
import datetime

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner = db.Column(db.String())
    repo = db.Column(db.String())
    branch = db.Column(db.String())

    def __init__(self, name,description,owner,repo,branch):
        self.name = name
        self.description = description
        self.owner = owner
        self.repo = repo
        self.branch = branch

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date,
            'likes':self.likes,
            'owner':self.owner,
            'repo':self.repo,
            'branch':self.branch,
        }

class Request(db.Model):
    __tablename__ = 'request'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String())
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, message, author, project):
        self.message = message
        self.author = author
        self.project_id = project

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'message': self.message,
            'author': self.author
        }


class Session(db.Model):
    __tablename__ = 'session'

    id         = db.Column(db.Integer, primary_key=True)
    owner      = db.Column(db.String())
    repo       = db.Column(db.String())
    branch     = db.Column(db.String())
    sha        = db.Column(db.String())
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    activemembers = db.Column(db.String())

    def __init__(self, owner, repo, branch, sha,project_id,activemembers):
        self.owner = owner,
        self.repo = repo,
        self.branch = branch,
        self.sha = sha,
        self.project_id = project_id,
        self.activemembers = activemembers

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'message': self.message,
            'author': self.author
        }




class TemFile(db.Model):
    __tablename__ = 'temfile'

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    path       = db.Column(db.String())
    content    = db.Column(db.String())
    sha        = db.Column(db.String())

    def __init__(self,session_id,path,content,sha):
        self.session_id = session_id
        self.path = path
        self.content = content
        self.sha = sha

    def __repr__(self):
        return '<id {}>'.format(self.id)



# class User(db.Model):
#     __tablename__ = 'user'

#     id         = db.Column(db.Integer, primary_key=True)
#     token      = db.Column(db.String())
#     username   = db.Column(db.String())

#     def __init__(self,token,username):
#         self.token = token
#         self.username = username















