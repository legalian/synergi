from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy
import requests
# from flask.ext.heroku import Heroku
import os


app = Flask(__name__)
socketio = SocketIO(app)
# heroku = Heroku(app)

# app.config.from_object(os.environ['APP_SETTINGS'])
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# from models import Book


@app.route("/template")
def templte():
	return render_template("/template.html")

@app.route("/")
def hello():
    return render_template("/index.html")

# @app.route("/add")
# def add_book():
#     name=request.args.get('name')
#     author=request.args.get('author')
#     published=request.args.get('published')
#     try:
#         book=Book(
#             name=name,
#             author=author,
#             published=published
#         )
#         db.session.add(book)
#         db.session.commit()
#         return "Book added. book id={}".format(book.id)
#     except Exception as e:
# 	    return(str(e))

# @app.route("/getall")
# def get_all():
#     try:
#         books=Book.query.all()
#         return  jsonify([e.serialize() for e in books])
#     except Exception as e:
# 	    return(str(e))

# @app.route("/get/<id_>")
# def get_by_id(id_):
#     try:
#         book=Book.query.filter_by(id=id_).first()
#         return jsonify(book.serialize())
#     except Exception as e:
# 	    return(str(e))

# @app.route("/add/form",methods=['GET', 'POST'])
# def add_book_form():
#     if request.method == 'POST':
#         name=request.form.get('name')
#         author=request.form.get('author')
#         published=request.form.get('published')
#         try:
#             book=Book(
#                 name=name,
#                 author=author,
#                 published=published
#             )
#             db.session.add(book)
#             db.session.commit()
#             return "Book added. book id={}".format(book.id)
#         except Exception as e:
#             return(str(e))
#     return render_template("getdata.html")




@app.route("/projectlist")
def projectlist():
	return render_template('todolist.html')


@app.route("/login")
def login():
	return "soidfjso"


@app.route("/logout")
def logout():
	return "jw9ejfoweufj"


@app.route("/editor")
def editor():
	return render_template('editor.html')


# @app.route("/projects",methods=['GET','POST'])
# @app.route("/projects/<int:id>",methods=['GET','PUT','DELETE'])


# @app.route("/projects/<int:id>/requests",methods=['GET','POST'])
# @app.route("/projects/<int:id>/requests/<int:rid>",methods=['DELETE'])



# @socketio.on('edit')
# def handle_my_custom_event(json):


@socketio.on('connect')
def handle_my_custom_connect():
	print("syjyyok")


@socketio.on('disconnect')
def on_disconnect():
	print('Client disconnected')


@socketio.on('edit')
def handle_edit(edit):
    emit('edit',edit,broadcast=True)





# def getfiles():
# 	response = requests.get("http://127.0.0.1:5000")






if __name__ == '__main__':
    socketio.run(app,debug=True)



