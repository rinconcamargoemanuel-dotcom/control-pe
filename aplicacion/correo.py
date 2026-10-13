"""
Envío de correos electrónicos (recordatorios de ARL).

IMPORTANTE: se usa la API de Brevo (HTTPS), NO el protocolo SMTP directo.
Render bloquea las conexiones SMTP salientes en su plan gratuito, así que
enviar por SMTP funciona en tu computador pero falla en producción. Usando
una API por HTTPS se evita ese bloqueo por completo.

Si el correo no se envía o da error, revisa únicamente este archivo y las
variables BREVO_API_KEY / EMAIL_REMITENTE en aplicacion/configuracion.py.
"""

import requests

from .configuracion import BREVO_API_KEY, EMAIL_REMITENTE, EMAIL_REMITENTE_NOMBRE

URL_API_BREVO = "https://api.brevo.com/v3/smtp/email"


def enviar_correo(destinatario, asunto, cuerpo_html):
    """
    Envía un correo mediante la API de Brevo. Devuelve (True, None) si
    salió bien, o (False, "mensaje de error") si algo falló — nunca lanza
    una excepción, para que un correo fallido no tumbe el resto del proceso.
    """
    if not BREVO_API_KEY or not EMAIL_REMITENTE:
        return False, "BREVO_API_KEY o EMAIL_REMITENTE no están configurados."

    payload = {
        "sender": {"name": EMAIL_REMITENTE_NOMBRE, "email": EMAIL_REMITENTE},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "htmlContent": cuerpo_html,
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        respuesta = requests.post(URL_API_BREVO, json=payload, headers=headers, timeout=10)
        if respuesta.status_code in (200, 201):
            return True, None
        return False, f"Brevo respondió {respuesta.status_code}: {respuesta.text}"
    except Exception as error:
        return False, str(error)


def correo_recordatorio_arl(nombre_estudiante, mes, anio):
    """Genera el asunto y el cuerpo HTML del recordatorio de ARL."""
    asunto = f"Recordatorio: falta cargar tu afiliación ARL de {mes}"
    cuerpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #123a63;">
        <h2>Control P.E — Recordatorio de afiliación ARL</h2>
        <p>Hola <strong>{nombre_estudiante}</strong>,</p>
        <p>
            Notamos que aún no has cargado tu certificado de afiliación ARL
            correspondiente a <strong>{mes} de {anio}</strong>.
        </p>
        <p>
            Ingresa al sistema y sube tu certificado desde la sección
            <strong>"ARL"</strong> para mantener tu proceso de prácticas
            empresariales al día.
        </p>
        <p style="color:#5a6472; font-size:0.85rem;">
            Este es un mensaje automático de Control P.E. Si ya la cargaste
            recientemente, puedes ignorar este correo.
        </p>
    </body>
    </html>
    """
    return asunto, cuerpo
