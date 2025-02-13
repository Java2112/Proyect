from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask import Flask, session  # ✅ Importar session


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__, static_folder="../app/static")  # ✅ Forzar la detección de `static/`
    app.config.from_object(Config)

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    
    @app.before_request
    def make_session_permanent():
        session.permanent = True  # ✅ Mantener la sesión activa

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import app_routes
    app.register_blueprint(app_routes)

    return app

    login_manager.login_view = "app_routes.login"  
    login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
    login_manager.login_message_category = "danger"

    from app.models import User 

    return app
