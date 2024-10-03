@echo off

rem Nombre del entorno virtual
set VENV_DIR=.venv

rem Nombre del archivo principal del programa
set MAIN_SCRIPT=main.py

rem Nombre del archivo de requerimientos
set REQUIREMENTS_FILE=requirements.txt

rem Nombre del archivo de entorno
set ENV_FILE=.env

rem Procesar opciones de línea de comandos
:parse_args
if "%~1"=="" goto end_parse_args
if "%~1"=="-e" (
    shift
    for %%A in (%1) do (
        for /f "tokens=1,2 delims==" %%B in (%%A) do (
            set "%%B=%%C"
        )
    )
)
shift
goto parse_args

:end_parse_args

rem Verifica si el entorno virtual ya existe
if not exist "%VENV_DIR%" (
    echo Entorno virtual no encontrado. Creando uno nuevo...

    rem Crea el entorno virtual
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error al crear el entorno virtual
        exit /b 1
    )

    echo Entorno virtual creado exitosamente.

    rem Activar el entorno virtual
    call "%VENV_DIR%\Scripts\activate.bat"

    rem Verificar si requirements.txt existe
    if exist "%REQUIREMENTS_FILE%" (
        echo Instalando dependencias desde %REQUIREMENTS_FILE%...
        pip install -r "%REQUIREMENTS_FILE%"
        if errorlevel 1 (
            echo Error al instalar dependencias
            exit /b 1
        )
    ) else (
        echo %REQUIREMENTS_FILE% no encontrado. Asegúrate de tener tus dependencias listadas.
        exit /b 1
    )
) else (
    echo Entorno virtual encontrado. Activando...
    call "%VENV_DIR%\Scripts\activate.bat"
)

rem Cargar variables de entorno desde .env si existe
if exist "%ENV_FILE%" (
    echo Cargando variables de entorno desde %ENV_FILE%...
    for /f "usebackq tokens=1,2 delims==" %%A in (`findstr /v "^#" "%ENV_FILE%"`) do (
        set "%%A=%%B"
    )
) else (
    echo %ENV_FILE% no encontrado. Asegúrate de tener las variables de entorno configuradas.
)

rem Sobrescribir o agregar variables de entorno adicionales pasadas con -e
echo Sobrescribiendo variables de entorno adicionales...
for /f "tokens=1,2 delims==" %%A in ('set') do (
    set "key=%%A"
    call echo %%key%%=%%B
)

rem Ejecutar el programa principal
if exist "%MAIN_SCRIPT%" (
    echo Ejecutando %MAIN_SCRIPT%...
    python "%MAIN_SCRIPT%"
) else (
    echo Archivo %MAIN_SCRIPT% no encontrado.
    exit /b 1
)

rem Desactivar el entorno virtual
deactivate
