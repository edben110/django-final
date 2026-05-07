from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import Reserva
from .forms import ReservaForm, CambiarEstadoForm


class ReservaListView(LoginRequiredMixin, ListView):
    """Lista de reservas del usuario (docente ve las suyas, admin ve todas)."""
    model = Reserva
    template_name = 'reservas/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        qs = Reserva.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(usuario=self.request.user)
        return qs


class ReservaCreateView(LoginRequiredMixin, CreateView):
    """Crear una nueva reserva (docente)."""
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:lista')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.estado = 'pendiente'
        messages.success(self.request, 'Reserva creada exitosamente.')
        return super().form_valid(form)


class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar reserva solo si está en estado Pendiente y es del usuario."""
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:lista')

    def test_func(self):
        reserva = self.get_object()
        # Solo el dueño puede editar y solo si está pendiente
        return (
            reserva.usuario == self.request.user and
            reserva.estado == 'pendiente'
        )

    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada exitosamente.')
        return super().form_valid(form)


class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Eliminar/cancelar reserva solo si está en estado Pendiente y es del usuario."""
    model = Reserva
    template_name = 'reservas/reserva_confirm_delete.html'
    success_url = reverse_lazy('reservas:lista')

    def test_func(self):
        reserva = self.get_object()
        return (
            reserva.usuario == self.request.user and
            reserva.estado == 'pendiente'
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Reserva cancelada exitosamente.')
        return super().delete(request, *args, **kwargs)


class CambiarEstadoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """El administrador puede aprobar o rechazar una reserva."""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['aprobada', 'rechazada']:
            reserva.estado = nuevo_estado
            reserva.save()
            messages.success(request, f'Reserva {nuevo_estado} exitosamente.')
        else:
            messages.error(request, 'Estado no válido.')
        return redirect('reservas:lista')
