import os

from flask import Flask, render_template, flash, redirect, session, request, g
import requests
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Favorite, Follows, Message
from forms import NewUserForm, LoginForm, UserEditForm, MessageForm
from flask_bcrypt import Bcrypt
from secret_key import api_key
from flask_debugtoolbar import DebugToolbarExtension

bcrypt = Bcrypt()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///phoodie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

resp_header = {'Authorization': 'bearer {}'.format(api_key)}

connect_db(app)
db.create_all()

API_BASE_SEARCH = 'https://api.yelp.com/v3/businesses/search'

@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/signup', methods=["GET", "POST"])
def signup():
    
    form = NewUserForm()
    if form.validate_on_submit():
           username=form.username.data
           password=form.password.data
           email=form.email.data
           image_url=form.image_url.data
           hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
           user = User(
                username=username,
                password=hashed_pwd,
                email=email,
                image_url=image_url)
           db.session.add(user)
           db.session.commit()
           session['username'] = user.username
           return redirect(f"/users/{user.id}")
    else:
           return render_template("signup.html", form=form)
       
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
   
    if CURR_USER_KEY in session:
        return redirect("/")
        
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)  
        if user:
            session[CURR_USER_KEY] = user.id
            return redirect("/")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("/login.html", form=form)

    return render_template("/login.html", form=form)     
       
                       
@app.route("/logout")
def logout():
    
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]   
    return redirect("/")


@app.route('/', methods=["GET"])
def showsearchform():
    return render_template("home.html")


@app.route('/results', methods=["GET"])
def searchresults():
    term = request.args["term"]
    location = request.args["location"]
    parameters = {'term': term, 'location' : location, 'limit' : 10}
    response = requests.get(API_BASE_SEARCH, params = parameters, headers = resp_header)
    data = response.json()
    businesses = data["businesses"]
    return render_template("home.html", businesses = businesses)

@app.route('/users')
def list_users():
    
 
 if g.user:
    
    following_ids = [f.id for f in g.user.following]
    me = User.query.get(g.user.id)
    following = me.following

    
    search = request.args.get('q')
    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users.html', users=users, following = following, following_ids = following_ids)
 else:
    return redirect("/")


@app.route('/users/<int:user_id>')
def user_detail(user_id):
    
  if g.user:
    
    following_ids = [f.id for f in g.user.following]
    me = User.query.get(g.user.id)
    following = me.following
    user = User.query.get(user_id)
    return render_template('userdetails.html', user=user, following = following, following_ids = following_ids)

  else:
    return redirect("/")



@app.route('/business/<business_id>')
def business_detail(business_id):
    response = requests.get(f"https://api.yelp.com/v3/businesses/{business_id}", headers = resp_header)
    response2 = requests.get(f"https://api.yelp.com/v3/businesses/{business_id}/reviews", headers = resp_header)
    data = response.json()
    data2 = response2.json()
    return render_template('businessdetails.html', data = data, data2 = data2)



@app.route('/business/<business_id>/add_favorites')
def add_favorite(business_id):
    response = requests.get(f"https://api.yelp.com/v3/businesses/{business_id}", headers = resp_header)
    data = response.json()
    name = data["name"]
    image_url = data["image_url"]
    address1 = data["location"]["address1"]
    city = data["location"]["city"]
    zip_code = data["location"]["zip_code"]
    state = data["location"]["state"]
    phone = data["phone"]
    user_id = g.user.id
    new_fave = Favorite(business_id = business_id, 
                        name = name,
                        image_url=image_url, 
                        address1=address1, 
                        city=city,
                        zip_code=zip_code,
                        state=state,
                        phone=phone, 
                        user_id = user_id)
    db.session.add(new_fave)
    db.session.commit()       
    return redirect(F"/business/{business_id}")

@app.route('/favorites')
def my_favorite():
    
    if not g.user:
        return redirect("/")
    
    user_id = g.user.id
    myfaves = Favorite.query.filter_by(user_id = user_id).all()   
    return render_template('favorites.html', myfaves = myfaves)


@app.route('/favorites/remove/<int:fave_id>',methods=["GET"])
def remove_favorite(fave_id):
    
    if not g.user:
        return redirect("/")
    
    myfaves = Favorite.query.get_or_404(fave_id)
    
    db.session.delete(myfaves)
    db.session.commit()
    return redirect("/favorites")

@app.route('/profile',methods=["GET"])
def profile():
    
    if not g.user:
        return redirect("/")
    user = User.query.get(g.user.id)
    return render_template('profile.html',  user =  user)


@app.route('/profile/update', methods=["GET", "POST"])
def update_profile():
    
    if not g.user:
        return redirect("/")
    
    user = g.user
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
      if User.authenticate(user.username, form.password.data):
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data or "https://gray-wafb-prod.cdn.arcpublishing.com/resizer/p77uuDSXvtiVo5BoAXByuRsD8yo=/1200x675/smart/filters:quality(85)/cloudfront-us-east-1.images.arcpublishing.com/gray/4JARI22Y55FDLAKTGYKV6J6Z6M.jpg"
        user.bio = form.bio.data
        user.location = form.location.data
        db.session.commit()
        return redirect("/profile")
    return render_template('update.html',  user=user, form = form)


@app.route('/users/follow/<int:following_id>', methods=["GET", "POST"])
def follow_users(following_id):
    if not g.user:
       return redirect("/")
        
    user_following_id = g.user.id
    user_being_followed_id = following_id
       
    new_follow = Follows(user_following_id = user_following_id, user_being_followed_id = user_being_followed_id)
    db.session.add(new_follow)
    db.session.commit()
       
    return redirect("/users")


@app.route('/following/', methods=["GET"])
def following():
    if not g.user:
       return redirect("/")
   
    user = User.query.get(g.user.id)
    following = user.following
          
    return render_template('following.html',  following = following)


@app.route('/messages/', methods=["GET", "POST"])
def messages():
    

    if not g.user:
       return redirect("/")
   
    form = MessageForm()
    
    messages = (Message.query.order_by(Message.timestamp.desc()).limit(100).all())
    user = g.user
   
    if form.validate_on_submit():
       user_id = user.id
       text = form.text.data
       image_url = form.image_url.data
       new_msg = Message(text = text, image_url = image_url,  user_id =  user_id )
       db.session.add(new_msg)
       db.session.commit()
       
       return redirect(f"/")

    return render_template('messages.html', messages = messages, form = form, user = user)


@app.route('/users/unfollow/<int:user_id>',methods=["GET"])
def remove_follow(user_id):
    
    if not g.user:
        return redirect("/")
    
    followed_user = User.query.get(user_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect("/users")
    
    
    
    
