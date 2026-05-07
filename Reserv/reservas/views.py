import csv
from io import StringIO
from urllib.parse import urlencode

from django.db.models import Count
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import Reserva
from .forms import ReservaForm, CambiarEstadoForm


def _reservas_base_queryset(user):
    qs = Reserva.objects.select_related('usuario').all()
    if not user.is_staff:
        qs = qs.filter(usuario=user)
    return qs


def _reservas_filtradas(request):
    qs = _reservas_base_queryset(request.user)
    fecha = request.GET.get('fecha', '').strip()
    laboratorio = request.GET.get('laboratorio', '').strip()

    if fecha:
        qs = qs.filter(fecha=fecha)
    if laboratorio:
        qs = qs.filter(laboratorio__icontains=laboratorio)

    return qs, fecha, laboratorio


class ReservaListView(LoginRequiredMixin, ListView):
    """Lista de reservas del usuario (docente ve las suyas, admin ve todas)."""
    model = Reserva
    template_name = 'reservas/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        qs, _, _ = _reservas_filtradas(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs, fecha, laboratorio = _reservas_filtradas(self.request)

        context['fecha_filtrada'] = fecha
        context['laboratorio_filtrado'] = laboratorio
        context['laboratorios_disponibles'] = (
            _reservas_base_queryset(self.request.user)
            .order_by('laboratorio')
            .values_list('laboratorio', flat=True)
            .distinct()
        )
        context['total_reservas'] = qs.count()
        context['reservas_pendientes'] = qs.filter(estado='pendiente').count()
        context['reservas_aprobadas'] = qs.filter(estado='aprobada').count()
        context['reservas_rechazadas'] = qs.filter(estado='rechazada').count()
        context['laboratorios_usados'] = qs.values('laboratorio').annotate(total=Count('id')).count()
        context['reservas_export_url'] = reverse('reservas:exportar_csv') + self._build_query_string()
        return context

    def _build_query_string(self):
        params = {}
        fecha = self.request.GET.get('fecha', '').strip()
        laboratorio = self.request.GET.get('laboratorio', '').strip()
        if fecha:
            params['fecha'] = fecha
        if laboratorio:
            params['laboratorio'] = laboratorio
        return f'?{urlencode(params)}' if params else ''


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


class ReservaExportCSVView(LoginRequiredMixin, View):
    def get(self, request):
        reservas = _reservas_filtradas(request)[0].order_by('-fecha_creacion')

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'usuario',
            'laboratorio',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'motivo',
            'fecha_creacion',
        ])

        for reserva in reservas:
            writer.writerow([
                reserva.usuario.username,
                reserva.laboratorio,
                reserva.fecha.isoformat(),
                reserva.hora_inicio.strftime('%H:%M:%S'),
                reserva.hora_fin.strftime('%H:%M:%S'),
                reserva.estado,
                reserva.motivo,
                reserva.fecha_creacion.isoformat(),
            ])

        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'
        return response
