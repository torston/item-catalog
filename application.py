from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_bootstrap import Bootstrap

from sqlalchemy import func

from database_setup import Base, User, Category, CatalogItem, engine

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import hashlib
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

APPLICATION_NAME = "Item Catalog Application"
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']


# show latest Items
@app.route('/')
@app.route('/index')
@app.route('/index.json', endpoint="index-json")
def home():
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    login_session['state'] = state

    items = session.query(CatalogItem).order_by(CatalogItem.id.desc()).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    categories = session.query(Category).all()

    return render_template('index.html',
                           categories=categories,
                           items=items,
                           logged_in=True,
                           section_title="Latest Items",
                           STATE=state,
                           )


# show Items
@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>.json', endpoint="item-json")
def category_items(category_name):
    print(category_name)
    category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

    if category is None:
        return jsonify('error, category not found')

    items = session.query(CatalogItem).filter_by(category_id=category.id).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    logged_in = True
    return render_template('index.html',
                           categories=[category],
                           current_category=category_name,
                           items=items,
                           logged_in=logged_in,
                           section_title="%s Items (%d items)" % (
                               category.name, len(items)),
                           )


# show Item details
@app.route('/catalog/<string:category_name>/<string:item_name>')
@app.route('/catalog/<string:category_name>/<string:item_name>.json', endpoint="category-json")
def item_details(category_name, item_name):
    category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

    if category is None:
        return jsonify('error, category not found')

    item = session.query(CatalogItem).filter(func.lower(CatalogItem.name) == func.lower(item_name)).first()

    if category is None:
        return jsonify('error, item not found')

    if request.path.endswith('.json'):
        return jsonify(item=item.serialize)

    logged_in = True
    return render_template('item_details.html',
                           item_name=item.name,
                           item_description=item.description,
                           logged_in=logged_in,
                           )

@app.route('/gconnect', methods=['POST'])
def gconnect():

    print('callback!')
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print( "done!")
    return output

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=8000)
