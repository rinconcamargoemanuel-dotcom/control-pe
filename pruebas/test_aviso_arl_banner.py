"""
Pruebas del aviso visual (banner) de ARL pendiente dentro de la página.
"""


def _crear_estudiante_y_loguear(cliente, email):
    cliente.post(
        "/registro",
        data={
            "nombre": "Estudiante Banner", "email": email,
            "password": "123456", "empresa": "Empresa", "grado": "11-6",
        },
        follow_redirects=True,
    )
    cliente.post("/login", data={"email": email, "password": "123456"}, follow_redirects=True)


def test_banner_aparece_si_no_ha_cargado_arl_este_mes(cliente):
    _crear_estudiante_y_loguear(cliente, "banner_sin_arl@test.com")
    respuesta = cliente.get("/dashboard")
    assert "Aún no has cargado tu afiliación ARL".encode("utf-8") in respuesta.data


def test_banner_no_aparece_si_ya_cargo_arl_este_mes(cliente):
    import io
    _crear_estudiante_y_loguear(cliente, "banner_con_arl@test.com")
    archivo_falso = (io.BytesIO(b"contenido"), "cert.pdf")
    cliente.post(
        "/arl",
        data={"mes": "Agosto", "anio": "2026", "archivo": archivo_falso},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    respuesta = cliente.get("/dashboard")
    assert "Aún no has cargado tu afiliación ARL".encode("utf-8") not in respuesta.data


def test_banner_no_aparece_para_administrador(cliente):
    cliente.post(
        "/login",
        data={"email": "admin@controlpe.edu.co", "password": "admin123"},
        follow_redirects=True,
    )
    respuesta = cliente.get("/dashboard")
    assert "Aún no has cargado tu afiliación ARL".encode("utf-8") not in respuesta.data
