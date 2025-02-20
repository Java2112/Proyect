import requests
import os
import time
from datetime import datetime
import pytz
from config import Config
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import yagmail
import zipfile
import json
import pandas as pd
from io import BytesIO

PROGRESO_PATH = "progreso.json"

def obtener_fachada(direccion, ciudad, estado, zip_code, filename):
    """Obtiene la imagen de la fachada usando la API de Google Street View con dirección más precisa."""
    api_key = Config.GOOGLE_API_KEY
    full_address = f"{direccion}, {ciudad}, {estado} {zip_code}"
    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {"size": "600x400", "location": full_address, "key": api_key}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        with open(image_path, "wb") as file:
            file.write(response.content)
        return image_path
    return None


def generar_pdfs(direcciones, imagenes, nombres, ciudades, estados, codigos_zip):
    """Genera un PDF individual para cada dirección con la imagen de la fachada al inicio."""

    upload_folder = Config.UPLOAD_FOLDER  # 📂 Define la carpeta de subida
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    pdf_paths = []

    for i, (direccion, imagen, nombre, ciudad, estado, zip_code) in enumerate(zip(direcciones, imagenes, nombres, ciudades, estados, codigos_zip)):
        filename = f"reporte_{i}.pdf"
        pdf_path = os.path.join(upload_folder, filename)
        pdf_paths.append(pdf_path)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # ✅ Insertar la imagen de la fachada al inicio
        if imagen and os.path.exists(imagen):
            img = ImageReader(imagen)
            c.drawImage(img, 50, height - 250, width=500, height=200, preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 270, "TIME FOR A NEW ROOF!")
        c.setFont("Helvetica-Bold", 14)
        full_address = f"{direccion}, {ciudad}, {estado} {zip_code}"
        c.drawCentredString(width / 2, height - 300, full_address)
        c.drawString(50, height - 330, f"Dear {nombre},")

        c.setFont("Helvetica", 11)
        mensaje = (
            "We are reaching out to you because we have identified that your property may "
            "have been affected by the recent storms that have impacted our community. At "
            "Royal Home Restoration, we specialize in inspecting and restoring storm-damaged "
            "roofs, and our commitment is to protect your home and your peace of mind."
        )
        c.drawString(50, height - 360, mensaje[:90])
        c.drawString(50, height - 375, mensaje[90:])

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 410, "Why are you receiving this letter?")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 430, "- Your neighborhood was impacted by recent storms.")
        c.drawString(50, height - 445, "- Roof damage isn't always visible but can lead to costly repairs.")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 480, "What do we offer?")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 500, "- FREE roof inspection by certified experts.")
        c.drawString(50, height - 515, "- A detailed report on your roof's condition.")
        c.drawString(50, height - 530, "- Guidance on repair/replacement options.")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 560, "Act now!")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 580, "Protect your greatest investment: your home.")
        c.drawString(50, height - 595, "Call us at (630) 383-1855")

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0, 0, 1)
        c.drawString(50, height - 610, "Visit us: https://royalhomerestoration.com")
        c.linkURL("https://royalhomerestoration.com", (50, height - 620, 300, height - 610))

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(50, height - 640, "Sincerely,")
        c.drawString(50, height - 655, "Sales Rep")
        c.drawString(50, height - 670, "Royal Home Restoration")
        c.drawString(50, height - 685, "Phone: (630) 383-1855")
        c.drawString(50, height - 700, "Email: info@royalhomerestoration.com")
        c.drawString(50, height - 715, "Address: 28 Garfield St, Oswego IL 60543")

        c.save()
        print(f"PDF generado: {pdf_path}")

    return pdf_paths  # ✅ Devuelve la lista de PDFs generados


def enviar_correo(destinatario, pdf_path, imagen_path, nombre, direccion, ciudad, estado, zip_code):
    """Envía un correo con el PDF y la imagen adjunta."""
    try:
        yag = yagmail.SMTP(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)

        asunto = "Your Roof Inspection Report"
        cuerpo = f"""
        <html>
        <body>
        <h2>TIME FOR A NEW ROOF!</h2>
        <p><b>Address:</b> {direccion}, {ciudad}, {estado} {zip_code}</p>
        <p>Dear {nombre},</p>
        <p>We are reaching out to you because we have identified that your property may have been affected by the recent storms 
        that have impacted our community.</p>
        <p>At Royal Home Restoration, we specialize in inspecting and restoring storm-damaged roofs, and our commitment is to 
        protect your home and your peace of mind.</p>

        <h3>Why are you receiving this letter?</h3>
        <ul>
            <li>Your neighborhood was impacted by recent storms.</li>
            <li>Roof damage isn't always visible but can lead to costly repairs.</li>
        </ul>

        <h3>What do we offer?</h3>
        <ul>
            <li>FREE roof inspection by certified experts.</li>
            <li>A detailed report on your roof's condition.</li>
            <li>Guidance on repair/replacement options.</li>
        </ul>

        <h3>Act now!</h3>
        <p>Protect your greatest investment: your home.</p>
        <p>Call us at (630) 383-1855 or visit our website: 
        <a href="https://royalhomerestoration.com">Royal Home Restoration</a></p>

        <h4>Sincerely,</h4>
        <p>Sales Rep<br>
        Royal Home Restoration<br>
        Phone: (630) 383-1855<br>
        Email: info@royalhomerestoration.com<br>
        Address: 28 Garfield St, Oswego IL 60543</p>
        </body>
        </html>
        """

        attachments = [pdf_path]
        if os.path.exists(imagen_path):
            attachments.append(imagen_path)  # ✅ Adjuntar la imagen si existe

        yag.send(to=destinatario, subject=asunto, contents=[cuerpo], attachments=attachments)
        print(f"Correo enviado a {destinatario} con {pdf_path} y {imagen_path}")
        return True
    except Exception as e:
        print(f"Error al enviar correo a {destinatario}: {str(e)}")
        return False

def cargar_progreso():
    """Carga los correos ya enviados desde el archivo JSON."""
    if os.path.exists(PROGRESO_PATH):
        with open(PROGRESO_PATH, "r") as file:
            return json.load(file)
    return {"enviados": []}  # Si el archivo no existe, iniciar con una lista vacía

def guardar_progreso(enviados):
    """Guarda la lista de correos enviados en el archivo JSON."""
    with open(PROGRESO_PATH, "w") as file:
        json.dump({"enviados": enviados}, file)

def enviar_correos_cada_30s(emails, pdfs, imagenes, nombres, direcciones, ciudades, estados, codigos_zip):
    """Envía correos cada 30 segundos, respetando el horario, aunque el correo esté repetido."""
    progreso = cargar_progreso()  # Cargar progreso
    enviados = progreso.get("enviados", [])  # Lista de correos ya enviados
    
    timezone_colombia = pytz.timezone("America/Bogota")

    for i in range(len(emails)):  # Recorrer todos los índices en lugar de "enumerate()"
        email = emails[i]

        # 🔹 No verifica si el correo está repetido, siempre lo envía
        while True:
            ahora = datetime.now(timezone_colombia).time()
            if 9 <= ahora.hour < 18:
                break
            print("⏳ Fuera del horario permitido. Esperando hasta las 9 AM...")
            time.sleep(60)

        inicio_envio = time.time()  # Captura el tiempo de inicio

        print(f"📩 Enviando correo a {email} ({i+1}/{len(emails)})...")
        if enviar_correo(email, pdfs[i], imagenes[i], nombres[i], direcciones[i], ciudades[i], estados[i], codigos_zip[i]):
            enviados.append(email)  # Se agrega el correo a la lista de enviados
            guardar_progreso({"enviados": enviados})  # Guarda el progreso
            print(f"✅ Correo enviado a {email}")
        else:
            print(f"❌ Error al enviar el correo a {email}")

        if i < len(emails) - 1:  # ⏳ Espera solo si hay más correos por enviar
            tiempo_transcurrido = time.time() - inicio_envio
            tiempo_restante = max(0, 30 - tiempo_transcurrido)  # Asegura que espere 30s exactos
            print(f"⏳ Esperando {int(tiempo_restante)} segundos antes del próximo envío...")
            time.sleep(tiempo_restante)

    print(f"✅ Se enviaron {len(enviados)} correos en esta ejecución.")
    return len(enviados)

def comprimir_pdfs(pdf_paths, zip_filename):
    """Comprime los PDFs en un archivo ZIP y lo devuelve."""
    zip_dir = Config.UPLOAD_FOLDER  # 📂 Carpeta de subida

    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)

    zip_path = os.path.join(zip_dir, zip_filename)

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for pdf in pdf_paths:
            if os.path.exists(pdf):  # ✅ Verifica que el archivo exista antes de agregarlo
                zipf.write(pdf, os.path.basename(pdf))
                print(f"✅ Agregado al ZIP: {pdf}")
            else:
                print(f"⚠️ Archivo no encontrado: {pdf}")

    return zip_path
