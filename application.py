from flask import Flask, render_template, url_for, flash
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
    open('client_secrets.json', 'r').read())['web']['client_id']


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

    logged_in = login_session.get("username", None) is not None

    print(logged_in)

    categories = session.query(Category).all()

    return render_template('index.html',
                           categories=categories,
                           items=items,
                           username=login_session.get("username", None),
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

    return render_template('index.html',
                           categories=[category],
                           current_category=category_name,
                           items=items,
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

    categories = session.query(Category).all()

    return render_template('item_details.html',
                           item=item,
                           categories=categories,
                           username=login_session.get("username", None),
                           )


@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def item_details_edit(category_name, item_name):
    category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

    if category is None:
        return jsonify('error, category not found')

    item = session.query(CatalogItem).filter(func.lower(CatalogItem.name) == func.lower(item_name)).first()

    if category is None:
        return jsonify('error, item not found')

    if request.path.endswith('.json'):
        return jsonify(item=item.serialize)

    categories = session.query(Category).all()

    if request.method == 'POST':
        print(request.form)
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = session.query(Category).filter(
            func.lower(Category.name) == func.lower(request.form['category_name'])).first()

        session.add(item)

        session.commit()

        flash('You were edited item!')

        return redirect(url_for('item_details',
                                category_name=item.category.name,
                                item_name=item.name))

    return render_template('item_details_edit.html',
                           item=item,
                           categories=categories,
                           username=login_session.get("username", None),
                           )


@app.route('/catalog/<string:category_name>/<string:item_name>/delete')
def item_details_delete(category_name, item_name):
    category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

    if category is None:
        return jsonify('error, category not found')

    item = session.query(CatalogItem).filter(func.lower(CatalogItem.name) == func.lower(item_name)).first()

    if category is None:
        return jsonify('error, item not found')

    session.delete(item)
    session.commit()

    return redirect(url_for('home'), code=301)


@app.route('/catalog/<string:category_name>/add', methods=['GET', 'POST'])
def item_details_add_category(category_name):
    if request.method == 'POST':
        item = CatalogItem()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = session.query(Category).filter(
            func.lower(Category.name) == func.lower(request.form['category_name'])).first()

        session.add(item)

        session.commit()

        return redirect(url_for('home'), code=301)

    else:
        category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

        item = CatalogItem()

        item.name = ''
        item.description = ''
        item.category = category
        categories = session.query(Category).all()

        return render_template('item_details_add.html',
                               item=item,
                               categories=categories,
                               category_name=category_name,
                               username=login_session.get("username", None),
                               )


@app.route('/catalog/add', methods=['GET', 'POST'])
def item_details_add():
    if request.method == 'POST':
        item = CatalogItem()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = session.query(Category).filter(
            func.lower(Category.name) == func.lower(request.form['category_name'])).first()

        session.add(item)

        session.commit()

        return redirect(url_for('home'), code=301)

    else:
        categories = session.query(Category).all()
        item = CatalogItem()

        item.name = ''
        item.description = ''

        return render_template('item_details_add.html',
                               item=item,
                               categories=categories,
                               username=login_session.get("username", None),
                               )


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print('callback!')
    flash('You were successfully logged in')
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
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('gplus_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'

        print("already connected!")
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = google_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    return jsonify(result='ok')


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'))
        response.headers['Content-Type'] = 'application/json'

        return redirect(url_for('home'), code=301)
    else:
        print('ERROR:')
        print(result)
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'

        return response


# @app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurantToDelete = session.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         session.delete(restaurantToDelete)
#         session.commit()
#         return redirect(
#             url_for('showRestaurants', restaurant_id=restaurant_id))
#     else:
#         return render_template(
#             'deleteRestaurant.html', restaurant=restaurantToDelete)
#     # return 'This page will be for deleting restaurant %s' % restaurant_id
#
#
# # Show a restaurant menu
# @app.route('/restaurant/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return render_template('menu.html', items=items, restaurant=restaurant)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=8000)
