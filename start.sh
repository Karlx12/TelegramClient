#!/bin/bash

# Nombre del entorno virtual
VENV_DIR=".venv"

# Nombre del archivo principal del programa
MAIN_SCRIPT="main.py"

# Nombre del archivo de requerimientos
REQUIREMENTS_FILE="requirements.txt"

# Nombre del archivo de entorno
ENV_FILE=".env"

# Variables de entorno adicionales pasadas por línea de comandos con -e
declare -A EXTRA_ENV_VARS

# Función para procesar opciones de línea de comandos
while getopts "e:" opt; do
    case $opt in
        e)
            IFS=',' read -ra PAIRS <<< "$OPTARG"
            for pair in "${PAIRS[@]}"; do
                IFS='=' read -ra KV <<< "$pair"
                EXTRA_ENV_VARS["${KV[0]}"]="${KV[1]}"
            done
            ;;
        *)
            echo "Uso: $0 [-e VAR1=valor1,VAR2=valor2,...]"
            exit 1
            ;;
    esac
done

# Verifica si el entorno virtual ya existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Entorno virtual no encontrado. Creando uno nuevo..."
    
    # Crea el entorno virtual
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Error al crear el entorno virtual"
        exit 1
    fi
    
    echo "Entorno virtual creado exitosamente."

    # Activar el entorno virtual
    source "$VENV_DIR/bin/activate"

    # Verificar si requirements.txt existe
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "Instalando dependencias desde $REQUIREMENTS_FILE..."
        pip install -r "$REQUIREMENTS_FILE"

        if [ $? -ne 0 ]; then
            echo "Error al instalar dependencias"
            exit 1
        fi
    else
        echo "$REQUIREMENTS_FILE no encontrado. Asegúrate de tener tus dependencias listadas."
        exit 1
    fi
else
    # Si el entorno virtual existe, solo se activa
    echo "Entorno virtual encontrado. Activando..."
    source "$VENV_DIR/bin/activate"
fi

# Cargar variables de entorno desde .env si existe
if [ -f "$ENV_FILE" ]; then
    echo "Cargando variables de entorno desde $ENV_FILE..."
    export $(grep -v '^#' "$ENV_FILE" | xargs -d '\n')
else
    echo "$ENV_FILE no encontrado. Asegúrate de tener las variables de entorno configuradas."
fi

# Sobrescribir o agregar variables de entorno adicionales pasadas con -e
echo "Sobrescribiendo variables de entorno adicionales..."
for key in "${!EXTRA_ENV_VARS[@]}"; do
    export "$key"="${EXTRA_ENV_VARS[$key]}"
    echo "Variable de entorno $key establecida como ${EXTRA_ENV_VARS[$key]}"
done

# Ejecutar el programa principal
if [ -f "$MAIN_SCRIPT" ]; then
    echo "Ejecutando $MAIN_SCRIPT..."
    python "$MAIN_SCRIPT"
else
    echo "Archivo $MAIN_SCRIPT no encontrado."
    exit 1
fi

# Desactivar el entorno virtual
deactivate
