import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class CodigoVerificacion(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='codigo_verificacion'
    )
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    intentos = models.IntegerField(default=0)

    def es_valido(self):
        """Expira a los 10 minutos."""
        return timezone.now() < self.creado_en + timedelta(minutes=10)

    def intentos_agotados(self):
        return self.intentos >= 5

    @classmethod
    def generar(cls, usuario):
        codigo = ''.join(random.choices(string.digits, k=6))
        obj, _ = cls.objects.update_or_create(
            usuario=usuario,
            defaults={
                'codigo': codigo,
                'creado_en': timezone.now(),
                'intentos': 0,
            }
        )
        return obj

    class Meta:
        verbose_name = 'Código de verificación'
        verbose_name_plural = 'Códigos de verificación'

    def __str__(self):
        return f'Código para {self.usuario.username}'
