from flask import Flask
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_sqlalchemy import SQLAlchemy

from flask_heroku import Heroku

# Initiate the Flask app with config
app = Flask(__name__, instance_relative_config=True)  # Heroku icin bunu False yap
app.config.from_object('config')
app.config.from_pyfile('config.py')  # Heroku icin bunu comment out et

# For Heroku
heroku = Heroku(app)

# Load bootstrap object
bootstrap = Bootstrap(app)

# Set database elements, start the tables
db = SQLAlchemy(app)

# Navbar (topbar)
nav = Nav()
topbar = Navbar(
    'Minty Fresh',
    View('Current', 'current'),
    View('History', 'history'),
    View('Sensor Data', 'showSensor'),
    View('Color Data', 'showColor'),
)

nav.register_element('top', topbar)
nav.init_app(app)

# For debugging
toolbar = DebugToolbarExtension(app)

# For circular dependencies
import fresh.views
