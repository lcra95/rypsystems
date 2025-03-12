import logging
import os

# Crear directorio de logs si no existe
log_dir = "app/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configuración del logger
logger = logging.getLogger("SSELogger")
logger.setLevel(logging.DEBUG)

# Formato del log
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')

# Salida del log a un archivo
file_handler = logging.FileHandler(f"{log_dir}/sse.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Salida del log a la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Agregar los handlers al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
