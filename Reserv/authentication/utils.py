from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def enviar_codigo_verificacion(usuario, codigo):
    asunto = 'Tu código de acceso — Sistema de Reservas'
    contexto = {
        'nombre': usuario.get_full_name() or usuario.username,
        'codigo': codigo,
        'expiracion': '10 minutos',
    }
    html_contenido = render_to_string(
        'emails/codigo_verificacion.html', contexto
    )
    texto_plano = (
        f'Hola {contexto["nombre"]}, tu código es: {codigo}. '
        f'Expira en {contexto["expiracion"]}.'
    )
    correo = EmailMultiAlternatives(
        subject=asunto,
        body=texto_plano,
        to=[usuario.email],
    )
    correo.attach_alternative(html_contenido, 'text/html')
    correo.send()
