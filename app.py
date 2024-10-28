from flask import Flask, render_template, request, session, redirect, flash
from functools import wraps
from dbUtils import *
from datetime import datetime
from werkzeug.utils import secure_filename
import os


# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static',static_url_path='/')
#set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#login page
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')
        if not loginID:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# login page and check
@app.route("/login")
def login():
    dat = getList()
    return render_template('login.html', data=dat)


@app.route('/check', methods=['POST'])
def check():
    form = request.form
    acc = form['ACC']
    pwd = form['PWD']
    dat = getLoginInfo(acc,pwd)
    if dat and acc == dat['user_account'] and pwd == dat['user_password']:
        session['loginID'] = dat['user_id']
        session['userName'] = dat['user_name']
        return redirect('/')
    else: 
        flash('Your account or password is wrong.')
        return redirect("/login")

#logout
@app.route('/logout', methods=['POST'])
def logout():
    session['loginID'] = None
    return redirect('/')

#regist
@app.route('/register')
def register():
    return render_template('register.html')   

#registing
@app.route('/registing', methods=['POST'])
def registing():
    form = request.form
    user_name = form['username']
    account = form['email']
    password = form['password']
    confirm_password = form['confirm_password']
    if password != confirm_password:
        flash("The password doesn't match")
        return redirect("register")
    addUser(user_name,account,password)
    return redirect("/login")

# home
@app.route('/')
def home():
    dat = getAllItems()
    return render_template('index.html',data = dat[:4], list_title="Hot Product")   

# auction list
@app.route('/auction')
def auction():
    dat = getAllItems()
    return render_template('auction.html',data=dat, list_title="Auction")

# item
@app.route('/item/<int:item_id>')
def item(item_id):
    item_dat = getItem(item_id)
    bid_dat = getBidInfo(item_id)
    loginState = session.get('loginID')
    time = datetime.now()
    return render_template("item.html",item = item_dat, bid = bid_dat, login = loginState, time = time) 

#add item
@app.route('/additem')
@login_required
def addItem():
    return render_template('additem.html')

#revise items
@app.route('/revise/<int:item_id>', methods=['GET','POST'])
@login_required
def revisePage(item_id):
    item = getItem(item_id)
    return render_template('revise.html', item = item)


#to specific user's product page
@app.route('/myproduct')
@login_required
def myProduct():
    user_id = session.get('loginID')
    product = getMyProduct(user_id)
    return render_template('myproduct.html', data=product, list_title="My Product")

#to specific user's bid product
@app.route('/mybid')
@login_required
def myBid():
    user_id = session.get('loginID')
    product = getMyBid(user_id)
    return render_template('mybid.html', data = product, list_title="My Bids")










#add product to db
@app.route('/additemtodb', methods=['GET','POST'])
@login_required
def addItemToDB():
    # store text info
    form = request.form
    item_name = form['ITEM_NAME']
    start_price = form['START_PRICE']
    dynasty = form['DYNASTY']
    material = form['MATERIAL']
    description = form['ITEM_DESCRIPTION']
    time = datetime.now()
    user_id = session.get('loginID')
    item_id = addItemDB(item_name,start_price, dynasty, material, description, time , user_id)
    file = request.files['UPLOAD']
    # store img
    if file and allowed_file(file.filename):
        file.filename = secure_filename(f"{item_id}.jpg")
        upload_path = os.path.abspath(os.path.dirname(__file__))
        upload_path = os.path.join(upload_path,'static', 'img', file.filename)
        file.save(upload_path)
    return redirect('/myproduct')

#delete item frome database
@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def deleteFromDB(item_id):
    deleteBid(item_id)
    deleteItem(item_id)
    return redirect('/myproduct')

#revise product to db
@app.route('/revisetodb', methods=['GET','POST'])
@login_required
def reviseToDB():
    # store text info
    form = request.form
    item_name = form['ITEM_NAME']
    start_price = form['START_PRICE']
    dynasty = form['DYNASTY']
    material = form['MATERIAL']
    description = form['ITEM_DESCRIPTION']
    time = datetime.now()
    user_id = session.get('loginID')
    item_id = reviseDB(item_name,start_price, dynasty, material, description, time , user_id)
    file = request.files['UPLOAD']
    # store img
    if file and allowed_file(file.filename):
        file.filename = secure_filename(f"{item_id}.jpg")
        upload_path = os.path.abspath(os.path.dirname(__file__))
        upload_path = os.path.join(upload_path,'static', 'img', file.filename)
        file.save(upload_path)
    return redirect('/myproduct')


#bid
@app.route('/bid', methods=['POST'])
@login_required
def bid():
    user_id = session.get('loginID')
    time = datetime.now()
    form = request.form
    price = form['PRICE']
    item_id = form['ITEM']
    tmp_item = getItem(item_id)
    max_price = tmp_item['max_price']
    if max_price == None: max_price = 0
    if float(price) <= float(max_price) or float(price) < float(tmp_item['start_price']):
        flash("Your bid need to be higher than current price!")
        return redirect(f"/item/{item_id}")
    addBid(item_id,user_id,price,time)
    return redirect(f"/item/{item_id}")
    
    
