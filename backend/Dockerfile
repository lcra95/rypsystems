# Usamos una imagen base de Python
FROM python:3.10-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiar los requisitos
COPY requirements.txt .

# Instalar los requisitos
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el contenido de la carpeta local (excepto lo ignorado) a /app
COPY . .

# Exponer el puerto 8800
EXPOSE 8800

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8800"]
