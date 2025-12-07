import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings


# ------------------------------------------------
# 📩 UTILIDAD PRINCIPAL: ENVIAR CORREOS
# ------------------------------------------------
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Envía un correo en formato HTML usando SMTP.
    Retorna True si fue exitoso, False si falló.
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        # Contenido HTML
        msg.attach(MIMEText(html_content, "html"))

        # Conexión SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())

        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


# ------------------------------------------------
# 🔑 CORREO PARA RECUPERAR CONTRASEÑA
# ------------------------------------------------
def send_password_reset_email(to_email: str, reset_code: str) -> bool:
    """
    Envía un correo con un código de recuperación de contraseña.
    """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2b6cb0;">🔐 Recuperación de contraseña</h2>
        <p>Has solicitado restablecer tu contraseña.</p>
        <p>Tu código de recuperación es:</p>
        <h1 style="color:#2b6cb0; background: #f0f4f8; padding: 15px; border-radius: 5px; text-align: center; letter-spacing: 5px;">
            {reset_code}
        </h1>
        <p style="color: #e53e3e;"><strong>⚠️ Este código expirará en 10 minutos.</strong></p>
        <p>Si no solicitaste este cambio, ignora este correo.</p>
        <hr>
        <p style="color: #718096; font-size: 12px;">
            Este es un correo automático, por favor no respondas a este mensaje.
        </p>
    </body>
    </html>
    """

    return send_email(
        to_email=to_email,
        subject="🔑 Código de recuperación de contraseña",
        html_content=html
    )