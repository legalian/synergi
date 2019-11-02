
import datetime
from app_factory import db
import hashlib
from sqlalchemy.dialects import postgresql as pg
def print(*args):
    sample = open('log.txt', 'a') 
    sample.write(' '.join([repr(k) if type(k) is not str else k for k in args])+'\n')
    sample.close()


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner = db.Column(db.String())
    repo = db.Column(db.String())
    branch = db.Column(db.String())
    write_access_users = db.Column(pg.ARRAY(db.String))

    def __init__(self, name, description, owner, repo, branch, write_access_users):
        self.name = name
        self.description = description
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.write_access_users = write_access_users

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date,
            'owner':self.owner,
            'repo':self.repo,
            'branch':self.branch,
            'write_access_users': self.write_access_users
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

    # all of the four most recent changes and their properties
    delta1_start=db.Column(db.Integer)
    delta1_amt = db.Column(db.Integer)
    delta1_data= db.Column(db.String())

    delta2_start=db.Column(db.Integer)
    delta2_amt = db.Column(db.Integer)
    delta2_data= db.Column(db.String())

    delta3_start=db.Column(db.Integer)
    delta3_amt = db.Column(db.Integer)
    delta3_data= db.Column(db.String())

    delta4_start=db.Column(db.Integer)
    delta4_amt = db.Column(db.Integer)
    delta4_data= db.Column(db.String())


    # 5 most recent md5 file hashes
    hash1      = db.Column(db.String())
    hash2      = db.Column(db.String())
    hash3      = db.Column(db.String())
    hash4      = db.Column(db.String())
    hash5      = db.Column(db.String())

    def addHash(self, md5, delta):#delta['start'],delta['amt'],delta['msg']
        def process(delt_start,delt_amt,delt_data):
            if(delt_start + delt_amt <= delta['start'] or delta['start'] + delta['amt'] <= delt_start): 
                if(delt_start < delta['start']):
                    delta['start'] += (len(delt_data) - delt_amt)
                return True


        ## find the matching md5 in the database
        # if not found, return false
        prev = False
        if md5==self.hash5:
            if not process(self.delta4_start, self.delta4_amt, self.delta4_data): return False
            prev = True
        if md5==self.hash4 or prev:
            if not process(self.delta3_start, self.delta3_amt, self.delta3_data): return False
            prev = True
        if md5==self.hash3 or prev:
            if not process(self.delta2_start, self.delta2_amt, self.delta2_data): return False
            prev = True
        if md5==self.hash2 or prev:
            if not process(self.delta1_start, self.delta1_amt, self.delta1_data): return False
            prev = True
        if not (prev or md5==self.hash1): return False
        ## if found update and shift
        self.content = self.content[:delta['start']]+delta['msg']+self.content[delta['start']+delta['amt']:]
        hash = hashlib.md5(self.content.encode("utf-8")).hexdigest()
        
        # shift hashes down one
        self.hash5 = self.hash4
        self.hash4 = self.hash3
        self.hash3 = self.hash2
        self.hash2 = self.hash1
        self.hash1 = hash

        # shift deltas down one
        self.delta4_start  = self.delta3_start  
        self.delta4_amt    = self.delta3_amt    
        self.delta4_data   = self.delta3_data   
        self.delta3_start  = self.delta2_start  
        self.delta3_amt    = self.delta2_amt    
        self.delta3_data   = self.delta2_data   
        self.delta2_start  = self.delta1_start  
        self.delta2_amt    = self.delta1_amt    
        self.delta2_data   = self.delta1_data   
        self.delta1_start  = delta['start']
        self.delta1_amt    = delta['amt']
        self.delta1_data   = delta['msg']
        return True

    def __init__(self,session_id,path,content,sha, md5):
        self.session_id = session_id
        self.path = path
        self.content = content
        self.sha = sha
        print("lil SUCCESS: ",md5)
        self.hash1 = md5
        self.hash2 = ""
        self.hash3 = ""
        self.hash4 = ""
        self.hash5 = ""
        

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















