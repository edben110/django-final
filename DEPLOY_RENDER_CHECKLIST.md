# ✅ Checklist Completo: Despliegue en Render - Sistema de Reservas

## 📋 Antes de Desplegar

- [x] `requirements.txt` en la raíz del repo
- [x] `.env` local configurado (pero **NO** subido a Git)
- [x] Rama actualizada (git push origin master)
- [x] settings.py configurado para producción
- [x] WhiteNoise configurado
- [x] Email backend robusto (maneja errores sin bloquear)

## 🔧 Configuración en Render Dashboard

### Step 1: Crear Web Service

1. Ve a **https://dashboard.render.com**
2. Click en **New +** → **Web Service**
3. Selecciona tu repositorio GitHub

### Step 2: Configurar el Servicio

```
Name: django-final
Branch: master (O LA RAMA DONDE TIENES TUS CAMBIOS)
Root Directory: (DEJAR VACÍO)
Runtime: Python 3
```

### Step 3: Build & Start Commands

**Build Command:**
```
pip install -r requirements.txt && python Reserv/manage.py collectstatic --noinput
```

**Start Command:**
```
gunicorn Reserv.wsgi --chdir Reserv --bind 0.0.0.0:$PORT --workers 3
```

### Step 4: Environment Variables (CRÍTICO)

En **Environment > Environment Variables**, añade EXACTAMENTE estos valores:

```
SECRET_KEY=django-insecure-generate-una-clave-aleatoria-de-50-caracteres
DEBUG=False
ALLOWED_HOSTS=django-final-h44m.onrender.com
DATABASE_URL=(COPIALO DEL PASO 5)
EMAIL_HOST_USER=(OPCIONAL - Gmail si quieres correos)
EMAIL_HOST_PASSWORD=(OPCIONAL - App password de Gmail)
```

### Step 5: Crear Base de Datos PostgreSQL

1. En Render Dashboard, click **Databases > New Database**
2. Selecciona **PostgreSQL**
3. Elige un nombre (ej: `reservas-db`)
4. Copia el `DATABASE_URL` que aparece
5. Pégalo en la variable de entorno `DATABASE_URL` del Web Service

## 🚀 Después de Crear el Servicio

### 1. Esperar a que termine el primer deploy

Los logs deberían mostrar:
```
==> Build successful
Starting service with 'gunicorn Reserv.wsgi --chdir Reserv...'
```

Si ves error 500, revisa los logs para detalles.

### 2. Ejecutar Migraciones

En Render Dashboard:
1. Ve a tu **Web Service > Shell**
2. Corre los comandos:

```bash
python Reserv/manage.py migrate
python Reserv/manage.py shell_plus
# (En el shell)
>>> from django.contrib.auth.models import User
>>> User.objects.all()  # Verificar que admin existe
>>> exit()
```

## 🔍 Troubleshooting

### ❌ Error: "python: can't open file '/opt/render/project/src/manage.py'"
**Causa:** Build Command intenta ejecutar `manage.py` en raíz del repo

**Solución:** Asegúrate que el Build Command sea:
```
pip install -r requirements.txt && python Reserv/manage.py collectstatic --noinput
```

### ❌ Error: HTTP 400 Bad Request
**Causa:** `ALLOWED_HOSTS` no incluye el dominio de Render

**Solución:** En Environment Variables, pon:
```
ALLOWED_HOSTS=django-final-h44m.onrender.com
```
(Reemplaza con tu dominio real)

### ❌ Error: HTTP 500 en POST /registro/
**Causas:**
1. Email backend no está configurado (SOLUCIONADO ahora con console backend)
2. Database no está migrada
3. Problema en la lógica del formulario

**Solución:**
- Revisa **Logs** en Render Dashboard
- Ejecuta migraciones si faltan
- Verifica que `DATABASE_URL` sea correcto

### ❌ Página de login vacía o con CSS roto
**Causa:** StaticFiles no se compiló correctamente

**Solución:**
```bash
# En Shell de Render:
python Reserv/manage.py collectstatic --clear --noinput
```

## 🔐 Security Checklist (Para Producción)

- [ ] Cambiar `SECRET_KEY` a un valor aleatorio (50+ caracteres)
- [ ] `DEBUG=False` está configurado
- [ ] Cambiar contraseña del admin (usuario: admin, actual: admin)
  ```bash
  # En Shell de Render:
  python Reserv/manage.py changepassword admin
  ```
- [ ] Configurar correo real (Gmail o SendGrid)
- [ ] Habilitar HTTPS (Render lo hace automáticamente)
- [ ] Revisar CORS si hay frontend separado
- [ ] Configurar backups de BD en Render

## 📱 URLs Importantes

- **App:** https://django-final-h44m.onrender.com (reemplaza con tu dominio)
- **Admin:** https://django-final-h44m.onrender.com/admin
- **Dashboard de Logs:** https://dashboard.render.com

## ✨ Flujo de Cambios Futuros

Después de tener todo deployado, para hacer cambios:

```bash
# 1. En local
git add .
git commit -m "Descripción del cambio"
git push origin master

# 2. Render redeploya automáticamente
# Puedes monitorear en https://dashboard.render.com/Logs

# 3. Si necesitas migraciones nuevas:
# Ve a Shell de Render y corre:
python Reserv/manage.py migrate
```

## 📞 Soporte

Si algo sigue fallando, verifica:
1. Los **Logs** en Render Dashboard (botón Logs)
2. Que `requirements.txt` esté actualizado
3. Que el `DATABASE_URL` sea correcto
4. Que `ALLOWED_HOSTS` incluya tu dominio
