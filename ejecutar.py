"""
Punto de entrada de la aplicación.

Uso local:
    python ejecutar.py

En producción (Render / gunicorn), se usa el objeto "app" directamente:
    gunicorn "ejecutar:app"
"""

import os

from aplicacion import crear_app

app = crear_app()

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    modo_debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=modo_debug, host="0.0.0.0", port=puerto)
