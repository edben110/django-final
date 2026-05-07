from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='lista'),
    path('crear/', views.ReservaCreateView.as_view(), name='crear'),
    path('editar/<int:pk>/', views.ReservaUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.ReservaDeleteView.as_view(), name='eliminar'),
    path('cambiar-estado/<int:pk>/', views.CambiarEstadoView.as_view(), name='cambiar_estado'),
]
