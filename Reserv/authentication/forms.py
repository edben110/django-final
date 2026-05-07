from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


ROL_CHOICES = [
    ('docente', 'Docente'),
    ('admin', 'Administrador'),
]


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'tu_correo@gmail.com'}),
        help_text='Se usará para enviar el código de verificación al iniciar sesión.'
    )
    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        required=True,
        label='Rol',
        help_text='Selecciona tu rol en el sistema.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'rol', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Si el rol es admin, marcar como staff
        if self.cleaned_data['rol'] == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False
        if commit:
            user.save()
        return user
