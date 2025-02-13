import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"  # ✅ Debe estar definido correctamente
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "app/uploads"  # ✅ Carpeta donde se guardarán los archivos subidos
    ALLOWED_EXTENSIONS = {"xlsx"}  # ✅ Solo permitimos archivos Excel
    GOOGLE_API_KEY = "AIzaSyBUChU82C1pXKNW7eedcfi3SI1j2ZB4bgA"


  # ✅ Configuración del correo
    EMAIL_SENDER = "Info@royalhomerestoration.com"  # 🔥 Tu correo de Gmail
    EMAIL_PASSWORD = "njay nzxl gzzq mpxt" 
