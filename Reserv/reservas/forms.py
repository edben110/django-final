from django import forms
from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'laboratorio': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        fecha = cleaned_data.get('fecha')
        laboratorio = cleaned_data.get('laboratorio')

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

        # Validar conflictos de horario en el mismo laboratorio
        if fecha and laboratorio and hora_inicio and hora_fin:
            conflictos = Reserva.objects.filter(
                laboratorio=laboratorio,
                fecha=fecha,
                estado__in=['pendiente', 'aprobada'],
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            for reserva in conflictos:
                if hora_inicio < reserva.hora_fin and hora_fin > reserva.hora_inicio:
                    raise forms.ValidationError(
                        f'Conflicto de horario: ya existe una reserva en {laboratorio} '
                        f'el {fecha} de {reserva.hora_inicio} a {reserva.hora_fin}.'
                    )

        return cleaned_data


class CambiarEstadoForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
