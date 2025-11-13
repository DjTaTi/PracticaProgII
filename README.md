# Aplicación de Cuestionario Flask

## Descripción
Aplicación web de cuestionarios que selecciona preguntas al azar de un archivo JSON y permite realizar exámenes interactivos.

## Archivos principales
- `app.py` - Aplicación Flask principal
- `questions.json` - Base de datos de preguntas
- `templates/` - Plantillas HTML
- `requirements.txt` - Dependencias Python
- `Procfile` - Configuración para Heroku

## Ejecución local
```bash
pip install -r requirements.txt
python app.py
```

## Despliegue en Heroku

### Paso 1: Preparación
1. Crear cuenta en [heroku.com](https://heroku.com)
2. Instalar [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Instalar Git si no lo tienes

### Paso 2: Inicializar repositorio Git
```bash
git init
git add .
git commit -m "Primera versión del cuestionario"
```

### Paso 3: Crear aplicación en Heroku
```bash
heroku login
heroku create tu-nombre-app
```

### Paso 4: Configurar variable de entorno
```bash
heroku config:set SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
```

### Paso 5: Desplegar
```bash
git push heroku main
```

### Paso 6: Abrir aplicación
```bash
heroku open
```

## Otras opciones de despliegue

### Render.com (Gratis)
1. Conectar repositorio de GitHub
2. Configurar como "Web Service"
3. Comando de construcción: `pip install -r requirements.txt`
4. Comando de inicio: `gunicorn app:app`

### PythonAnywhere (Gratis con limitaciones)
1. Subir archivos via web interface
2. Configurar WSGI file
3. Configurar static files

### Railway (Fácil)
1. Conectar GitHub repo
2. Deploy automático

## Configuración adicional para producción
- Cambiar `SECRET_KEY` por una clave segura
- Considerar base de datos para preguntas más grandes
- Agregar autenticación si es necesario
- Configurar dominio personalizado