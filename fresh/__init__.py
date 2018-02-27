from flask import Flask
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_sqlalchemy import SQLAlchemy

from flask_heroku import Heroku

# Initiate the Flask app with config
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# For Heroku
heroku = Heroku(app)

# Load bootstrap object
bootstrap = Bootstrap(app)

# Set database elements, start the tables
db = SQLAlchemy(app)
from database import init_db
init_db()

# Navbar (sidebar)
nav = Nav()
sidebar = Navbar(
    'Minty Fresh',
    View('Home', 'mainpage'),
    View('Monitor', 'showData'),
)

nav.register_element('left', sidebar)
nav.init_app(app)

# For debugging
toolbar = DebugToolbarExtension(app)

# For circular dependencies
import fresh.views
