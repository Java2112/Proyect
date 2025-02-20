import os
import time
import pandas as pd
from flask import render_template, redirect, url_for, flash, send_file, session, request, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, UploadForm
from app.utils import obtener_fachada, generar_pdfs, enviar_correo, enviar_correos_cada_30s, comprimir_pdfs
from flask_bcrypt import Bcrypt
from config import Config

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
                df.columns = df.columns.str.strip().str.lower()  # Normaliza nombres de columnas

                columnas_necesarias = {
                    "address": None,
                    "name": None,
                    "email": None,
                    "city": None,
                    "state": None,
                    "zip": None
                }

                for col in df.columns:
                    col_lower = col.lower()
                    if col_lower in columnas_necesarias:
                        columnas_necesarias[col_lower] = col

                if None in columnas_necesarias.values():
                    faltantes = [key for key, val in columnas_necesarias.items() if val is None]
                    flash(f"⚠️ El archivo Excel no tiene las columnas necesarias: {', '.join(faltantes)}.", "danger")
                    return redirect(url_for("app_routes.upload_file"))

                direcciones = df[columnas_necesarias["address"]].astype(str).tolist()
                nombres = df[columnas_necesarias["name"]].astype(str).tolist()
                emails = df[columnas_necesarias["email"]].astype(str).tolist()
                ciudades = df[columnas_necesarias["city"]].astype(str).tolist()
                estados = df[columnas_necesarias["state"]].astype(str).tolist()
                codigos_zip = df[columnas_necesarias["zip"]].astype(str).tolist()

                # 🔹 Imprimir datos para depuración
                print("✅ DIRECCIONES:", direcciones)
                print("✅ NOMBRES:", nombres)
                print("✅ EMAILS:", emails)
                print("✅ CIUDADES:", ciudades)
                print("✅ ESTADOS:", estados)
                print("✅ CÓDIGOS ZIP:", codigos_zip)

                imagenes = []
                for i, (direccion, ciudad, estado, zip_code) in enumerate(zip(direcciones, ciudades, estados, codigos_zip)):
                    imagen_nombre = f"fachada_{i}.jpg"
                    imagen_path = obtener_fachada(direccion, ciudad, estado, zip_code, imagen_nombre)
                    imagenes.append(imagen_path)

                pdf_paths = generar_pdfs(direcciones, imagenes, nombres, ciudades, estados, codigos_zip)

                # 🔹 Enviar correos con 30 segundos de intervalo
                correos_enviados = enviar_correos_cada_30s(emails, pdf_paths, imagenes, nombres, direcciones, ciudades, estados, codigos_zip)

                flash(f"✅ Se enviaron {correos_enviados} correos con sus respectivos PDFs.", "success")
                return redirect(url_for("app_routes.upload_file"))

            except Exception as e:
                flash(f"❌ Error al procesar el archivo: {str(e)}", "danger")

    return render_template("upload.html", form=form)

@app_routes.route("/download_reports", methods=["GET"])
@login_required
def download_reports():
    pdf_folder = Config.UPLOAD_FOLDER  # 📂 Ruta donde se guardan los PDFs
    zip_filename = "reportes_comprimidos.zip"

    # 🔹 Obtener la lista de archivos PDF en la carpeta de subida
    pdf_paths = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    if not pdf_paths:
        flash("⚠️ No hay reportes disponibles para descargar.", "warning")
        return redirect(url_for("app_routes.upload_file"))

    zip_path = comprimir_pdfs(pdf_paths, zip_filename)  # 📦 Comprime los PDFs encontrados

    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    else:
        flash("❌ Error al generar el ZIP.", "danger")
        return redirect(url_for("app_routes.upload_file"))

@app_routes.route("/dashboard")
def dashboard():
    return "Bienvenido al dashboard"

@app_routes.route("/")
def home():
    return render_template("index.html")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS