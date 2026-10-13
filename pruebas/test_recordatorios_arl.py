"""
Pruebas del módulo de recordatorios automáticos de ARL.
"""

import os


def test_endpoint_recordatorio_rechaza_token_incorrecto(cliente):
    respuesta = cliente.get("/tareas/recordatorio-arl?token=token_falso")
    assert respuesta.status_code == 403


def test_endpoint_recordatorio_acepta_token_correcto(cliente, app):
    token_real = app.config.get("TOKEN_TAREAS") or os.environ.get(
        "TOKEN_TAREAS", "cambia-este-token-por-uno-propio"
    )
    respuesta = cliente.get(f"/tareas/recordatorio-arl?token={token_real}")
    # Aunque el envío de correo real falle (no hay SMTP configurado en pruebas),
    # el endpoint debe responder 200 con el resumen de resultados.
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert "total_recordatorios_enviados" in datos
    assert "detalle" in datos

