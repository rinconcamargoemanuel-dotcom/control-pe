# CONTROL P.E — Sistema de Control de Prácticas Empresariales

Aplicación web basada en el proyecto **CONTROL P.E** (I.E. José Joaquín Flórez Hernández, SENA — Grado 11-6).
Digitaliza el proceso descrito en el documento: registro de horas/bitácora, carga de evidencias,
control de afiliación mensual a la ARL, y revisión/validación por parte de docentes y coordinadores.

## Tecnologías
- **Backend:** Python 3 + Flask (organizado en módulos con Blueprints)
- **Base de datos:** MySQL (las tablas se crean solas al ejecutar por primera vez)
- **Frontend:** HTML + CSS (plantillas Jinja2)

## Estructura del proyecto

Todo está separado por carpetas y archivos en español según su función. Si algo falla,
solo hay que revisar el archivo responsable de esa parte — no hay que buscar en un único
archivo gigante.

```
control_pe/
├── ejecutar.py                    # Punto de entrada: "python ejecutar.py"
├── requirements.txt                # Dependencias
├── Procfile                        # Comando de arranque para Render
├── CUMPLIMIENTO_METAS.md           # Cruce entre el documento de metas y lo implementado
├── basedatos/
│   ├── crear_base_datos.sql        # Crea la base de datos MySQL real
│   └── crear_base_datos_pruebas.sql # Crea la base de datos separada para pruebas
├── pruebas/
│   ├── conftest.py                 # Configuración de pytest (usa la BD de pruebas)
│   └── test_flujo_completo.py      # Pruebas de login, horas, evidencias, validación, etc.
└── aplicacion/
    ├── __init__.py                 # Arma la app y conecta cada módulo
    ├── configuracion.py            # Claves, datos de conexión MySQL, correo, listas fijas
    ├── base_datos.py                # Conexión MySQL + creación de tablas + usuarios de prueba
    ├── auxiliares.py                # Decoradores de permisos (login, roles) y validaciones
    ├── correo.py                     # Envío de correos electrónicos (recordatorios de ARL)
    ├── rutas/                       # Cada archivo = una sección del sistema
    │   ├── autenticacion.py         #   login, registro, logout, perfil
    │   ├── panel.py                 #   pantalla de inicio (dashboard) por rol
    │   ├── horas.py                 #   bitácora de horas del estudiante
    │   ├── evidencias.py            #   evidencias del estudiante
    │   ├── arl.py                   #   afiliación ARL mensual del estudiante
    │   ├── estudiantes.py           #   ver detalle y aprobar/rechazar registros
    │   ├── usuarios.py              #   gestión de usuarios (solo administrador)
    │   └── tareas.py                #   recordatorios automáticos de ARL por correo
    ├── plantillas/                  # Vistas HTML, organizadas por sección
    │   ├── base.html                #   plantilla compartida (menú, pie de página)
    │   ├── perfil.html
    │   ├── autenticacion/
    │   │   ├── login.html
    │   │   └── registro.html
    │   ├── panel/
    │   │   ├── estudiante.html
    │   │   └── personal.html
    │   ├── horas/horas.html
    │   ├── evidencias/evidencias.html
    │   ├── arl/arl.html
    │   ├── estudiantes/ver.html
    │   └── usuarios/
    │       ├── lista.html
    │       └── nuevo.html
    └── estaticos/
        ├── css/
        │   └── estilos.css          # Colores, tipografía, estilos generales
        └── imagenes/
            ├── notas_diseno.txt      # "Bloc de notas": documenta colores, fuente e imágenes
            ├── logo/                 # Logo del sistema (si se agrega uno)
            ├── iconos/               # Iconos propios (si se dejan de usar emojis)
            └── subidas/              # Evidencias y certificados ARL cargados (automático)
```

### ¿Dónde corrijo qué?

| Si el problema es sobre...              | Revisa el archivo...                          |
|------------------------------------------|-----------------------------------------------|
| Iniciar sesión, registro, mi perfil       | `aplicacion/rutas/autenticacion.py`            |
| La pantalla de inicio tras entrar         | `aplicacion/rutas/panel.py`                    |
| Registro de horas                         | `aplicacion/rutas/horas.py`                    |
| Subir evidencias                          | `aplicacion/rutas/evidencias.py`               |
| Afiliación ARL                            | `aplicacion/rutas/arl.py`                      |
| Ver/aprobar/rechazar a un estudiante      | `aplicacion/rutas/estudiantes.py`              |
| Crear/eliminar usuarios                   | `aplicacion/rutas/usuarios.py`                 |
| Tablas o columnas de la base de datos     | `aplicacion/base_datos.py`                     |
| Permisos (quién puede entrar a dónde)     | `aplicacion/auxiliares.py`                     |
| Claves, rutas de carpetas                 | `aplicacion/configuracion.py`                  |
| Apariencia (colores, estilos)             | `aplicacion/estaticos/css/estilos.css`         |
| El diseño de una pantalla específica      | el `.html` correspondiente en `plantillas/`    |

## Base de datos MySQL — configuración inicial

Este proyecto usa **MySQL** en vez de un archivo local. Antes de ejecutar la
aplicación por primera vez:

1. **Instala MySQL** en tu computador si no lo tienes:
   - Windows: [MySQL Installer](https://dev.mysql.com/downloads/installer/) (elige "MySQL Server").
   - Durante la instalación, define una contraseña para el usuario `root` y anótala.

2. **Crea la base de datos vacía** (una sola vez). Desde la terminal, dentro
   de la carpeta del proyecto:
   ```bash
   mysql -u root -p < basedatos/crear_base_datos.sql
   ```
   (te pedirá la contraseña de `root` que definiste al instalar MySQL)

3. **Indica tus credenciales a la aplicación** mediante variables de entorno.
   En Windows (CMD), antes de ejecutar la app:
   ```cmd
   set MYSQL_USUARIO=root
   set MYSQL_PASSWORD=tu_contraseña_de_mysql
   set MYSQL_BASE_DATOS=control_pe
   ```
   En Mac/Linux:
   ```bash
   export MYSQL_USUARIO=root
   export MYSQL_PASSWORD=tu_contraseña_de_mysql
   export MYSQL_BASE_DATOS=control_pe
   ```
   Si no defines estas variables, la app intentará conectarse a
   `localhost`, usuario `root`, sin contraseña (ver `aplicacion/configuracion.py`).

Las **tablas** (`usuarios`, `horas`, `evidencias`, `arl`) y los **3 usuarios
de prueba** se crean automáticamente la primera vez que ejecutes la app —
no necesitas crearlas a mano.

## Meta de horas y seguimiento

El sistema muestra una **barra de progreso** con las horas acumuladas del
estudiante frente a la meta exigida (por defecto, 80 horas). Se puede
ajustar con la variable de entorno `META_HORAS`, por ejemplo:
```bash
export META_HORAS=120
```
Esta meta se ve tanto en el panel del propio estudiante como en el
listado que ven docentes/coordinadores/administrador (con buscador por
nombre incluido).

## Pruebas automatizadas (Semana 3 del proyecto)

El proyecto incluye pruebas automatizadas en la carpeta `pruebas/` que
verifican que todo el flujo funciona: inicio de sesión, registro de
horas, carga de evidencias, aprobación/rechazo por el docente, seguimiento
de horas, y permisos por rol.

Usan una **base de datos separada** (`control_pe_pruebas`) para no tocar
nunca los datos reales:

```bash
# Una sola vez:
mysql -u root -p < basedatos/crear_base_datos_pruebas.sql
pip install -r requirements.txt

# Cada vez que quieras verificar que todo funciona:
pytest pruebas/ -v
```
Resultado esperado: `8 passed`.

Ver `CUMPLIMIENTO_METAS.md` para el detalle de qué prueba corresponde a
cada punto del documento de metas de entrega.

## Recordatorios automáticos de ARL por correo

El sistema puede enviar un correo automático a cada estudiante que **no
haya cargado su ARL del mes actual**.

⚠️ **Importante:** se usa **Brevo** (un servicio de envío de correos por
API), no Gmail/SMTP directo. Esto es porque Render bloquea las conexiones
salientes por SMTP en su plan gratuito — un correo enviado por SMTP
funciona perfecto en tu computador, pero falla con "timeout" en la versión
pública. Brevo envía por HTTPS, así que no tiene ese problema.

### 1. Crea tu cuenta gratuita en Brevo

1. Ve a [brevo.com](https://www.brevo.com) y crea una cuenta gratis
   (incluye 300 correos gratis por día, más que suficiente para esto).
2. Verifica tu correo y completa el registro.
3. Dentro del panel de Brevo, ve a tu perfil (ícono arriba a la derecha) →
   **"SMTP & API"** → pestaña **"API Keys"**.
4. Clic en **"Generate a new API key"**, ponle un nombre (ej. "Control PE"),
   y copia la clave que te genera (empieza con `xkeysib-...`).
5. Ve a **"Senders"** (remitentes) y agrega/verifica el correo desde el
   cual quieres que salgan los recordatorios (por ejemplo tu propio Gmail)
   — Brevo te pedirá confirmar ese correo antes de poder usarlo como remitente.

### 2. Define las variables de entorno

```bash
set BREVO_API_KEY=xkeysib-tu-clave-completa-aqui
set EMAIL_REMITENTE=tu_correo_verificado@gmail.com
set TOKEN_TAREAS=elige-un-texto-secreto-y-dificil-de-adivinar
```
(en Render, agrégalas en "Environment Variables" en vez de `set`)

### 3. Envío manual (sin configurar nada extra)

Cualquier docente, coordinador o administrador puede hacer clic en el botón
**"📧 Enviar recordatorios de ARL ahora"** en el Panel de seguimiento — envía
el correo en el momento a todos los estudiantes que aún no hayan cargado la
ARL de este mes.

### 4. Envío automático diario (opcional, sin que nadie tenga que acordarse)

Para que se envíe solo, todos los días, sin que ningún docente tenga que
hacer clic en nada:

1. Ve a [cron-job.org](https://cron-job.org) y crea una cuenta gratis.
2. Crea un nuevo "Cronjob" con esta URL (reemplaza con tu dominio real y tu
   `TOKEN_TAREAS`):
   ```
   https://tu-app.onrender.com/tareas/recordatorio-arl?token=TU_TOKEN_SECRETO
   ```
3. Configura que se ejecute, por ejemplo, todos los días a las 8:00 a.m.
4. Listo — cron-job.org "visita" esa URL todos los días, y el sistema envía
   los correos solo a quien le falte la ARL de ese mes (a quien ya la subió
   no le llega nada).

⚠️ Si tu app está en el plan gratuito de Render, recuerda que "duerme" tras
inactividad — la primera visita del día puede tardar unos segundos extra en
responder mientras el servicio despierta, eso es normal.

## Instalación y ejecución

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación (con las variables de entorno de MySQL ya definidas):
   ```bash
   python ejecutar.py
   ```
3. Abrir en el navegador: **http://localhost:5000**

Al ejecutar por primera vez, se crea automáticamente la base de datos SQLite con 3 usuarios de prueba:

| Rol           | Correo                          | Contraseña   |
|---------------|----------------------------------|--------------|
| Administrador | admin@controlpe.edu.co           | admin123     |
| Docente       | docente@controlpe.edu.co         | docente123   |
| Coordinador   | coordinador@controlpe.edu.co     | coord123     |

Los **estudiantes** se registran libremente desde "Regístrate aquí" en la pantalla de inicio de sesión.

## Roles y funcionalidades (según el documento del proyecto)

- **Estudiante:** registra horas/bitácora, sube evidencias de actividades, carga mensualmente el
  certificado de afiliación ARL, y consulta el estado de aprobación de cada registro.
- **Docente Supervisor / Coordinador:** consultan el listado de estudiantes, revisan el detalle
  de cada uno (horas, evidencias, ARL) y **aprueban o rechazan** cada registro.
- **Administrador:** gestiona los usuarios del sistema (crear/eliminar).

## Base de datos

Tablas principales (MySQL), definidas en `aplicacion/base_datos.py`:
- `usuarios` (estudiantes, docentes, coordinadores, administradores)
- `horas` (registros de bitácora con estado Pendiente/Aprobado/Rechazado)
- `evidencias` (archivos cargados por el estudiante)
- `arl` (certificados de afiliación mensual a la ARL)

## Diseño gráfico e imágenes

Todo lo visual está organizado en `aplicacion/estaticos/`:
- `css/estilos.css` — colores, tipografía y estilos generales.
- `imagenes/notas_diseno.txt` — el "bloc de notas" del diseño: paleta de
  colores, tipografía usada, e inventario de cada imagen (dónde está
  guardada y en qué plantilla se usa). **Actualiza este archivo cada vez
  que agregues o cambies una imagen**, para que quede documentado.
- `imagenes/logo/` y `imagenes/iconos/` — carpetas listas para cuando
  agregues un logo o iconos propios.
- `imagenes/subidas/` — se llena sola con lo que suben los estudiantes
  (evidencias y certificados ARL); no se edita a mano.

## Notas
- Las contraseñas se almacenan con hash seguro (Werkzeug `generate_password_hash`).
- Los archivos subidos (evidencias, ARL) se guardan en `aplicacion/estaticos/imagenes/subidas/`.
- Para producción, define la variable de entorno `SECRET_KEY` (ver más abajo) y no actives `FLASK_DEBUG`.
- **No subas tu contraseña de MySQL a GitHub.** Usa siempre variables de entorno
  (`MYSQL_USUARIO`, `MYSQL_PASSWORD`, etc.), nunca las escribas directamente en el código.

## Desplegar en Render (para que cualquier persona entre desde internet)

1. Sube esta carpeta a un repositorio de **GitHub** (puede ser privado o público).
2. Entra a [render.com](https://render.com) y crea una cuenta (puedes usar tu cuenta de GitHub).
3. Clic en **New +** → **Web Service**.
4. Conecta tu repositorio de GitHub.
5. Configura:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "ejecutar:app"`
6. En la sección **Environment Variables**, agrega:
   - `SECRET_KEY` → cualquier texto largo y aleatorio (por ejemplo, generado con `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `MYSQL_HOST`, `MYSQL_PUERTO`, `MYSQL_USUARIO`, `MYSQL_PASSWORD`, `MYSQL_BASE_DATOS` → los datos de tu base de datos MySQL en la nube (ver siguiente punto).
7. **Necesitas una base de datos MySQL accesible desde internet** — Render ya no
   ofrece MySQL gratuito propio, así que puedes usar un proveedor externo con
   plan gratuito, por ejemplo [Railway](https://railway.app),
   [Aiven](https://aiven.io) o [FreeSQLDatabase](https://www.freesqldatabase.com).
   Ellos te darán el host, usuario, contraseña y nombre de base de datos para
   llenar las variables de entorno del punto anterior.
   - Los archivos subidos (`aplicacion/estaticos/imagenes/subidas/`) sí dependen del
     disco de Render, que no persiste entre reinicios en el plan gratuito. Si esto es
     importante, considera un **Persistent Disk** (plan pago) o subir esos archivos
     a un servicio externo (por ejemplo, Cloudinary o un bucket S3).
8. Clic en **Create Web Service**. Render te dará una URL pública como `https://control-pe.onrender.com`, accesible desde cualquier red o país.

### Alternativa rápida (PythonAnywhere)
Si prefieres algo aún más simple para SQLite con persistencia real gratuita, [PythonAnywhere](https://www.pythonanywhere.com) también funciona bien con Flask y mantiene tus archivos entre sesiones sin necesidad de configurar disco aparte.
