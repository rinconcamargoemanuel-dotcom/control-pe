@echo off
REM ============================================================
REM  CONTROL P.E - Iniciar TODO con un doble clic
REM  (servidor + pagina web + diagrama de la base de datos)
REM ============================================================
REM  Antes de usar este archivo por primera vez:
REM  1. Ajusta la ruta de la carpeta del proyecto mas abajo si es
REM     distinta (busca la linea que empieza con "cd /d").
REM  2. Reemplaza "TU_CONTRASENA_AQUI" por tu contrasena real de MySQL.
REM  3. Genera el diagrama UNA VEZ en Workbench (Ctrl+R) y guardalo
REM     como .mwb (File > Save Model As...). Ajusta su ruta en la
REM     linea "MYSQL_DIAGRAMA" mas abajo.
REM  4. Si MySQL Workbench esta instalado en otra ruta, ajusta la
REM     linea "MYSQL_WORKBENCH_EXE" mas abajo.
REM ============================================================

title Control P.E - Servidor

set MYSQL_WORKBENCH_EXE="C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe"
set MYSQL_DIAGRAMA="E:\proyecto 1.2\control_pe_v8\diagrama_control_pe.mwb"

cd /d "C:\Users\Anderson\Documents\proyecto 1.2\control_pe_v8"
pip install -r requirements.txt

set MYSQL_USUARIO=root
set MYSQL_PASSWORD=emanuel1130
set MYSQL_BASE_DATOS=control_pe

echo.
echo Abriendo el diagrama de la base de datos...
if exist %MYSQL_DIAGRAMA% (
    start "" %MYSQL_WORKBENCH_EXE% %MYSQL_DIAGRAMA%
) else (
    echo [Aviso] No se encontro el archivo del diagrama en la ruta configurada.
    echo Genera el diagrama una vez en Workbench ^(Ctrl+R^), guardalo como .mwb,
    echo y ajusta la linea MYSQL_DIAGRAMA en este .bat con su ruta real.
)

echo.
echo Iniciando el servidor de Control P.E en segundo plano...
start "Control P.E - Servidor" cmd /k python ejecutar.py

echo.
echo Esperando a que el servidor arranque...
timeout /t 5 /nobreak >nul

echo.
echo Abriendo la pagina web...
start "" http://localhost:5000

echo.
echo Todo listo. Esta ventana ya puede cerrarse.
echo El servidor sigue corriendo en su propia ventana ^("Control P.E - Servidor"^);
echo no la cierres mientras uses el sistema.
echo.
pause >nul
