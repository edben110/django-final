Pasos para desplegar en Render (Django + Postgres)

1. Subir el repo a GitHub/GitLab/Bitbucket y conectar al panel de Render.

2. Crear un "Web Service" en Render:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: dejar vacío (Render usará el `Procfile`) o usar `gunicorn Reserv.wsgi --chdir Reserv --bind 0.0.0.0:$PORT --workers 3`
   - Branch: la rama que quieras desplegar

3. Crear una base de datos Postgres en Render (Add > PostgreSQL):
   - Guardar la `DATABASE_URL` que Render provee.

4. En el Web Service, añadir las variables de entorno (Environment > Environment Variables):
   - `DATABASE_URL` = (la URL de Postgres de la DB creada)
   - `SECRET_KEY` = una clave secreta segura
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `your-app.onrender.com`
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (si usas envío de correos)

5. Migraciones y collectstatic:
   - En el Dashboard de Render, usa la opción "Shell" o crea un `one-off` command para ejecutar:
     - `python Reserv/manage.py migrate`
     - `python Reserv/manage.py collectstatic --noinput`

6. Verificar logs y probar la app.

Notas:
- No uses SQLite en Render porque el filesystem es efímero; por eso configuramos `DATABASE_URL` hacia Postgres.
- Si cambias la estructura del proyecto, ajusta `--chdir` en el `Procfile`.
