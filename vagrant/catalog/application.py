from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from repository import UserRepository, CategoryItemRepository, CategoryRepository

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from google.oauth2 import id_token
from google.auth.transport import requests
import httplib2
import json
from flask import make_response

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Application"

userRepository = UserRepository()
categoryItemRepository = CategoryItemRepository()
categoryRepository = CategoryRepository()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route("/googleconnect", methods=['GET', 'POST'])
def googleconnect():
    print("----------------->>>>>>>>>>>>>    step 0   <<<<<<<<<<<<<-----------------")

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print("----------------->>>>>>>>>>>>>    step 1   <<<<<<<<<<<<<-----------------")

    access_token = request.data

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            access_token, requests.Request(), CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        usertokenid = idinfo['sub']

        # Save user name to login session
        userId = userRepository.getUserID(idinfo['email'])

        if userId is not None:
            currentUser = userRepository.readById(userId)
            login_session['username'] = currentUser.name
            login_session['email'] = currentUser.email
            login_session['picture'] = currentUser.picture
            login_session['access_token'] = usertokenid
        else:
            login_session['username'] = idinfo['name']
            login_session['email'] = idinfo['email']
            login_session['picture'] = idinfo['picture']
            login_session['access_token'] = usertokenid
            userRepository.create(
                login_session['username'], login_session['email'], login_session['picture'])

    except ValueError:
        # Invalid token
        pass

    output = ''
    output += '<h1>Welcome' + str(login_session['username']) + '!'
    output += '<h4>You are logged in with email: ' + \
        str(login_session['email']) + '</h4>'
    return output


@app.route('/gdisconnect', methods=['GET', 'POST'])
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['login_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return 'You have benn logged out'


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = userRepository.getUserID(login_session['email'])
    if not user_id:
        user_id = userRepository.create(
            login_session['username'], login_session['email'], login_session['picture'])
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    items = categoryItemRepository.readAllByCategoryId(category_id)
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
    item = categoryItemRepository.readByCategoryId(category_id, item_id)
    return jsonify(CategoryItem=item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = categoryRepository.readAll()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = categoryRepository.readAll()
    if 'username' not in login_session:
        print('public template')
        return render_template('publicCategories.html', categories=categories)
    else:
        print('private template')
        return render_template('categories.html', categories=categories)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        userId = userRepository.getUserID(login_session['email'])
        categoryRepository.create(name=request.form['name'], user_id=userId)
        flash('New Category Successfully Created')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            categoryRepository.update(category_id, request.form['name'])
            flash('Category Successfully Edited')
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)

# Show a category item
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def showItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    if 'username' not in login_session:
        creator = getUserInfo(category.user_id)
        print('with creator')
        return render_template('publicItem.html', items=items, category=category, creator=creator)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        print('with user')
        return render_template('item.html', items=items, category=category, user=user)


# Create a new item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newCategoryItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategoryItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            category_id=category_id,
            user_id=getUserID(login_session['email']))
        session.add(newItem)
        session.commit()
        flash('New Item %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template('newCategoryItem.html', category_id=category_id)


# Edit a item item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Item Item Successfully Edited')
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template('editCategoryItem.html', category_id=category_id, item_id=item_id, item=editedItem)


# Delete a item item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Item Successfully Deleted')
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.env = 'development'
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
