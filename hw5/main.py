
from flask import Flask, request, send_from_directory, render_template,session, redirect,url_for
from flask_login import login_required, login_user, LoginManager, UserMixin,logout_user
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = b'hello'
login_manager = LoginManager()
login_manager.init_app(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/users"
mongo = PyMongo(app)

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'static/upload/')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(UserMixin):
    def __init__(self, username, password):
        self.password = password
        self.username = username

    def is_active(self):
        return True
    
    def get(self,username):
        if self.username == username:
            return self
        else:
            return None

    def get_id(self):
        return self.username


def check_passwd(username,password,password_db):
    if password == password_db:
        return User(username,password)
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.user.find_one({"username": username})
        if user is not None:
            user = check_passwd(username,password,user['password'])
        if user is not None:
            user = login_user(user)
            return redirect(url_for('cabinet'))
    return render_template('login.html')
    
@app.route('/cabinet', methods=['POST', 'GET'])
@login_required
def cabinet():

    if request.method == 'POST':
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('cabinet.html', filename=filename)
    return render_template('cabinet.html')
    
@app.route('/11.jpg')
def im3():
    return app.send_static_file('11.jpg')
      
@app.route('/static/')
def imgg(path):
    return send_from_directory('static', path)
    
@login_manager.user_loader
def load_user(username):
    user = mongo.db.user.find_one({"username": username})
    if user is not None:
        return User(username,user['password'])
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)