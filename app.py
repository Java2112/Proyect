from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.routes import app_routes
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)



app = create_app()  # Asegura que estamos usando la función create_app()
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, static_folder="app/static")  # ✅ Asegurar que Flask sirva `static/`
