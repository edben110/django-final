from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.contrib import messages


# --- Autenticación ---

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('reserva_list')


class RegisterView(FormView):
    template_name = 'authentication/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Cuenta creada exitosamente. Bienvenido!')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reserva_list')
        return super().dispatch(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
