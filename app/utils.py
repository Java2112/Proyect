import requests
import os
from config import Config
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import yagmail

def obtener_fachada(direccion, filename):
    """Obtiene la imagen de la fachada usando la API de Google Street View."""
    api_key = Config.GOOGLE_API_KEY
    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": "600x400",  # Tamaño de la imagen
        "location": direccion,
        "key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        with open(image_path, "wb") as file:
            file.write(response.content)
        print(f"Imagen guardada: {image_path}")
        return image_path
    else:
        print(f"Error al obtener la imagen: {response.status_code}")
        return None


def generar_pdfs(datos, imagenes, nombres):
    """Genera un PDF individual para cada dirección con la imagen de la fachada al inicio."""
    pdf_paths = []

    for i, (direccion, imagen_path, nombre) in enumerate(zip(datos, imagenes, nombres)):
        filename = f"reporte_{i}.pdf"
        pdf_path = os.path.join("app/uploads", filename)
        pdf_paths.append(pdf_path)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # ✅ Insertar la imagen de la fachada al inicio
        if os.path.exists(imagen_path):
            img = ImageReader(imagen_path)
            c.drawImage(img, 50, height - 250, width=500, height=200, preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 270, "TIME FOR A NEW ROOF!")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 300, direccion)
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


def enviar_correo(destinatario, pdf_path, imagen_path, nombre, direccion):
    """Envía un correo con el PDF y la imagen adjunta."""
    try:
        yag = yagmail.SMTP(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)

        asunto = "Your Roof Inspection Report"
        cuerpo = f"""
        <html>
        <body>
        <h2>TIME FOR A NEW ROOF!</h2>
        <p><b>Address:</b> {direccion}</p>
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