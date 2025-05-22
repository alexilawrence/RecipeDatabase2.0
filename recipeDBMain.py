import pymongo
import os
from dotenv import load_dotenv
import sys
import datetime
import flask
from flask import Flask, url_for, request, session, redirect
import bcrypt
from bcrypt import hashpw, gensalt, checkpw
from functools import wraps

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = datetime.timedelta(minutes=60) #sessions close after 60min

mongClient = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(mongClient)
db = client.myDatabase

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods = ["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        desiredPage = request.form['pageName']
        if desiredPage == 'View':
            coll = db.get_collection('recipes')
            names = []
            data = coll.find({'userID':{'$eq':session['userID']}})
            for doc in data:
                names.append(doc['recipeName'])
                
            if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
                
                
            return flask.render_template('view.html', names=names)
        
        elif desiredPage == 'Create':
            return flask.render_template('create.html')
        
        
        
        elif desiredPage == 'Edit':
            coll = db.get_collection('recipes')
            names = []
            data = coll.find({'userID':{'$eq':session['userID']}})
            for doc in data:
                names.append(doc['recipeName'])
                
            if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
            
            return flask.render_template('edit.html', names=names)
        
        
        elif desiredPage == 'Delete':
            coll = db.get_collection('recipes')
            names = []
            data = coll.find({'userID':{'$eq':session['userID']}})
            for doc in data:
                names.append(doc['recipeName'])
                
            if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
            
            return flask.render_template('Delete.html', names=names)
        
    else:
        return flask.render_template('home.html', username = session['username'])
        
@app.route('/view', methods = ['GET', "POST"])
@login_required
def view():
    if request.method == "POST":
        recipeName = request.form['recipe']
        if recipeName == 'No recipes added. Click me to return to the home page':
            return flask.render_template('home.html', username = session['username'])
        
        else:
            #return recipeName, along with the actual recipe (Decide how its gonnna be done)
            coll = db.get_collection('recipes')
            
            recipe = coll.find_one({
                'recipeName':{'$eq': recipeName},
                'userID':{'$eq': session['userID']}
                })
            
            quantities = recipe['quantities']
            components = recipe['components']
            procedures = recipe['procedures']
            tips = recipe['tips']
            ingredients = []
            
            for i in range(len(components)):
                ingredients.append(f"{quantities[i]}, {components[i]}")      
            
        
            cleanedProcedures = []
            for procedure in procedures.splitlines():
                procedure = procedure.strip()
                if procedure:
                    cleanedProcedures.append(procedure)
            cleanedTips = [tip.strip() for tip in tips.strip().splitlines()]
            
            enumeratedProcedures = []
            for i in range(len(cleanedProcedures)):
                num = i + 1
                enumeratedProcedures.append(f"{num}. {cleanedProcedures[i]}")
        

            
            return flask.render_template('viewRecipe.html', recipeName=recipeName, ingredients=ingredients, procedures=enumeratedProcedures, tips=cleanedTips)
        
        
    else:
        coll = db.get_collection('recipes')
        names = []
        data = coll.find({'userID':{'$eq':session['userID']}})
        for doc in data:
            names.append(doc['recipeName'])
            
        if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
                
        return flask.render_template('view.html', names = names)
    
@app.route('/view/<recipeName>', methods=["GET", "POST"])
def viewRecipe(recipeName):
    return flask.render_template('home.html', username = session['username'])
    
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        recipeName = request.form['recipeName']
        ingredients = request.form['ingredients']
        procedures = request.form['procedures']
        tips = request.form['tips']
        
        #get collection
        coll = db.get_collection('recipes')
        
        #clean up the ingredients list
        quantities = []
        components = []
        for i in ingredients.splitlines():
            i = i.strip()
            if i:
                splitted = i.split(sep="|")
                print(splitted)
                quantities.append(splitted[0].strip())
                components.append(splitted[1].strip())
            
        #insert the data into the collection
        coll.insert_one({'userID': session['userID'],'recipeName': recipeName, 'quantities':quantities, 'components':components, 'procedures': procedures, 'tips':tips})
        
        #return the user to the 'view' page
        names = []
        data = coll.find({'userID':{'$eq':session['userID']}})
        for doc in data:
            names.append(doc['recipeName'])
        return flask.render_template('view.html', names=names)
    
    return flask.render_template('create.html')


@app.route('/delete', methods= ['GET', 'POST'])
@login_required
def delete():
    if request.method == "POST":
        recipeName = request.form['recipe']
        if recipeName == 'No recipes added. Click me to return to the home page':
            return flask.render_template('home.html', username = session['username'])
        
        else:
            return flask.render_template('confirmDelete.html', recipeName=recipeName)
        
    else:
        coll = db.get_collection('recipes')
        names = []
        data = coll.find({'userID':{'$eq':session['userID']}})
        for doc in data:
            names.append(doc['recipeName'])
            
        if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
        return flask.render_template('delete.html', names = names)
    
@app.route('/confirmDelete', methods=["GET", "POST"])
@login_required
def confirmDelete():
    if request.method=="POST":
        decision = request.form['decision']
        if decision != 'no':
            coll = db.get_collection('recipes')
            coll.delete_one({
                'recipeName':{'$eq': decision},
                'userID':{'$eq': session['userID']}
                })
        
    return flask.render_template('home.html')

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method=="POST":
        recipeName = request.form['recipe']
        if recipeName == 'No recipes added. Click me to return to the home page':
            return flask.render_template('home.html', username = session['username'])
        
        else:
            coll = db.get_collection('recipes')
            recipe = coll.find_one({
                    'recipeName':{'$eq': recipeName},
                    'userID':{'$eq': session['userID']}
                    })
            quantities = recipe['quantities']
            components = recipe['components']
            procedures = recipe['procedures']
            tips = recipe['tips']
            
            ingredients = ''
            for i in range(len(quantities)):
                ingredients += f"{quantities[i]} | {components[i]}\n"
            return flask.render_template('editPage.html', recipeName=recipeName, ingredients=ingredients, procedures=procedures, tips=tips)
    else:
        coll = db.get_collection('recipes')
        names = []
        data = coll.find({'userID':{'$eq':session['userID']}})
        for doc in data:
            names.append(doc['recipeName'])
            
        if len(names) == 0:
                names = ['No recipes added. Click me to return to the home page']
                
        return flask.render_template('edit.html', names = names)
            
@app.route('/editPage', methods=['GET','POST'])
@login_required
def editPage():
    recipeName = request.form['recipeName']
    ingredients = request.form['ingredients']
    procedures = request.form['procedures']
    tips = request.form['tips']
    
    #get collection
    coll = db.get_collection('recipes')
    
    #clean up the ingredients list
    quantities = []
    components = []
    for i in ingredients.splitlines():
        i = i.strip()
        if i:
            splitted = i.split(sep="|")
            print(splitted)
            quantities.append(splitted[0].strip())
            components.append(splitted[1].strip())
        
    #delete the original record
    coll.delete_one({
                'recipeName':{'$eq': recipeName},
                'userID':{'$eq': session['userID']}
                })
    #insert the data into the collection
    coll.insert_one({'userID': session['userID'],'recipeName': recipeName, 'quantities':quantities, 'components':components, 'procedures': procedures, 'tips':tips})
    
    
    return flask.render_template('home.html', username = session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        #get collection
        coll = db.get_collection('users')
        user = coll.find_one({'username':{'$eq': username}})
        if user == None:
            return flask.render_template('login.html', error='Invalid username. Please sign up if you do not have an existing account.')
        
        elif checkpw(password.encode('utf-8'), user['password']) == False:
            return flask.render_template('login.html', error='Invalid password. Please try again or aproach admin for help.')
        else:
            session['username'] = username #save the user's session
            
            #save the UserID to the session
            session['userID'] = user['userID']
            
            next_page = request.args.get('next') #get the original page (the one that led you to login)
            return redirect(next_page) if next_page else redirect('/')
        
    else:
        return flask.render_template('login.html')
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method =='POST':
        coll = db.get_collection('users')
        username = request.form['username']
        password = request.form['password']
        encryptedPW = hashpw(password.encode('utf-8'), gensalt())
        
        #generate a userID
        num = coll.count_documents({})
        userID = num
        
        coll.insert_one({'username':username, 'password':encryptedPW, 'userID':userID})
        return redirect('/login')
    
    else:
        return flask.render_template('signup.html')
if __name__ == "__main__":
    app.run(port=5000)