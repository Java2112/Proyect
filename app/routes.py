import os
from flask import render_template, redirect, url_for, flash
from flask import Blueprint
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, UploadForm
from flask_bcrypt import Bcrypt
from flask import Blueprint, render_template
from werkzeug.utils import secure_filename
from config import Config
from flask_login import login_required, current_user
import pandas as pd
from flask_login import login_user, logout_user, login_required, current_user
from app.utils import obtener_fachada, generar_pdfs, enviar_correo
from flask import send_file, request
from flask import session



app_routes = Blueprint("app_routes", __name__)
bcrypt = Bcrypt()

@app_routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Tu cuenta ha sido creada. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("app_routes.login"))
    return render_template("register.html", form=form)

@app_routes.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)

            # ✅ Verificar si ya se ha mostrado el mensaje antes de agregarlo
            if "_flashes" not in session or not any("Inicio de sesión exitoso" in msg for msg, _ in session["_flashes"]):
                flash("Inicio de sesión exitoso.", "success")

            return redirect(url_for("app_routes.upload_file"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html", form=form)

@app_routes.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(file_path)

            try:
                df = pd.read_excel(file_path, engine="openpyxl")

                columnas_direccion = ["Address", "Dirección"]
                columna_nombre = "Name"
                columna_email = "Email"  # ✅ Nueva columna para el correo

                if not any(col in df.columns for col in columnas_direccion):
                    flash("El archivo Excel no tiene una columna 'Address' o 'Dirección'.", "danger")
                    return redirect(url_for("app_routes.upload_file"))

                if columna_nombre not in df.columns or columna_email not in df.columns:
                    flash("El archivo Excel no tiene las columnas 'Name' y 'Email'.", "danger")
                    return redirect(url_for("app_routes.upload_file"))

                columna_direccion = next(col for col in columnas_direccion if col in df.columns)
                direcciones = df[columna_direccion].tolist()
                nombres = df[columna_nombre].tolist()
                emails = df[columna_email].tolist()  # ✅ Lista de correos electrónicos

                imagenes = []
                for i, direccion in enumerate(direcciones):
                    imagen_nombre = f"fachada_{i}.jpg"
                    imagen_path = obtener_fachada(direccion, imagen_nombre)
                    imagenes.append(imagen_path)

                pdf_paths = generar_pdfs(direcciones, imagenes, nombres)

                # ✅ Enviar cada PDF al correo correspondiente
                correos_enviados = 0
                for i, pdf in enumerate(pdf_paths):
                    if enviar_correo(emails[i], pdf, imagenes[i], nombres[i], direcciones[i]):  # ✅ Indentación corregida
                        correos_enviados += 1  # ✅ Ahora está bien indentado dentro del if

                flash(f"Se enviaron {correos_enviados} correos con sus respectivos PDFs.", "success")
                return redirect(url_for("app_routes.upload_file"))

            except Exception as e:
                flash(f"Error al procesar el archivo: {str(e)}", "danger")

    return render_template("upload.html", form=form)



@app_routes.route("/download_pdf/<filename>")
@login_required
def download_pdf(filename):
    pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    return send_file(pdf_path, as_attachment=True)


@app_routes.route("/dashboard")
def dashboard():
    return "Bienvenido al dashboard"

@app_routes.route("/")
def home():
    return render_template("index.html")

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

