import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

alchemy = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.secret_key = "super secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    alchemy.init_app(app)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return "Hello World!"
    
    from . import db
    db.init_app(app)

    from . import home
    app.register_blueprint(home.bp)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import calendar_user
    app.register_blueprint(calendar_user.bp)
    
    from . import calendar_admin
    app.register_blueprint(calendar_admin.bp)

    
    return app 
#from flask import Flask
#from flask_cors import CORS
#from .config import Config

#def create_app():
  #  app = Flask(__name__, template_folder='../templates')  # Point to templates folder
  #  app.config.from_object(Config)
   # CORS(app)
    
 #   from .routes import main
 #   app.register_blueprint(main)
    
 #   return app