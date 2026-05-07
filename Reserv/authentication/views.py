from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegistroForm
from .models import CodigoVerificacion
from .utils import enviar_codigo_verificacion


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            # Guardar el pk en sesión sin autenticar todavía
            request.session['usuario_pendiente_2fa'] = usuario.pk
            # Generar y enviar código
            obj = CodigoVerificacion.generar(usuario)
            enviar_codigo_verificacion(usuario, obj.codigo)
            return redirect('verificar_codigo')
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'authentication/login.html', {'error': error})


def verificar_codigo_view(request):
    pk = request.session.get('usuario_pendiente_2fa')
    if not pk:
        return redirect('login')

    try:
        usuario = User.objects.get(pk=pk)
        obj = CodigoVerificacion.objects.get(usuario=usuario)
    except (User.DoesNotExist, CodigoVerificacion.DoesNotExist):
        return redirect('login')

    error = None

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()

        if obj.intentos_agotados():
            error = 'Demasiados intentos fallidos. Inicia sesión nuevamente.'
            del request.session['usuario_pendiente_2fa']
            obj.delete()
        elif not obj.es_valido():
            error = 'El código expiró. Inicia sesión nuevamente para obtener uno nuevo.'
            del request.session['usuario_pendiente_2fa']
            obj.delete()
        elif obj.codigo == codigo_ingresado:
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
            del request.session['usuario_pendiente_2fa']
            obj.delete()
            return redirect('reserva_list')
        else:
            obj.intentos += 1
            obj.save()
            restantes = 5 - obj.intentos
            error = f'Código incorrecto. Te quedan {restantes} intento(s).'

    # Enmascarar el correo para mostrar en pantalla
    email = usuario.email
    if email:
        partes = email.split('@')
        if len(partes[0]) > 2:
            visible = partes[0][0] + '***' + partes[0][-1]
        else:
            visible = partes[0][0] + '***'
        email_mascarado = visible + '@' + partes[1]
    else:
        email_mascarado = '(sin correo registrado)'

    return render(request, 'authentication/verificar_codigo.html', {
        'email_mascarado': email_mascarado,
        'error': error,
    })


def reenviar_codigo_view(request):
    pk = request.session.get('usuario_pendiente_2fa')
    if not pk:
        return redirect('login')

    usuario = User.objects.get(pk=pk)
    obj = CodigoVerificacion.generar(usuario)
    enviar_codigo_verificacion(usuario, obj.codigo)
    return redirect('verificar_codigo')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('reserva_list')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente. ¡Bienvenido!')
            return redirect('reserva_list')
    else:
        form = RegistroForm()

    return render(request, 'authentication/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
