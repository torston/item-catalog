from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import func

from database_setup import Base, User, Category, CatalogItem, engine

app = Flask(__name__)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

APPLICATION_NAME = "Item Catalog Application"


# show latest Items
@app.route('/')
@app.route('/index')
@app.route('/index.json', endpoint="index-json")
def home():
    items = session.query(CatalogItem).order_by(CatalogItem.id.desc()).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    categories = session.query(Category).all()

    return render_template('index.html',
                           categories=categories,
                           items=items,
                           logged_in=True,
                           section_title="Latest Items",
                           )


# show Items
@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>.json', endpoint="category-json")
def category_items(category_name):
    print(category_name)
    category = session.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()

    if category is None:
        return jsonify('error, category not found')

    items = session.query(CatalogItem).filter_by(category_id=category.id).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    categories = session.query(Category).all()

    logged_in = True
    return render_template('index.html',
                           categories=categories,
                           current_category=category_name,
                           items=items,
                           logged_in=logged_in,
                           section_title="%s Items (%d items)" % (
                               category_name, len(items)),
                           )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
