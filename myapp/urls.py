from django.urls import path
from . import views

urlpatterns = [
    path('servicio/', views.solicitar_servicio),
    path('peticiones/', views.peticiones),
    path('ayuda/', views.ayuda),
    path('reset/', views.reset),
    path('detalles/', views.detalles),
    path('resumen/', views.resumen),
    path('solicitudes/', views.solicitudes),
    path('export/', views.exportar_detalles),
    path('export_resume/', views.exportar_resumen),
    path('informacion/', views.informacion),
    path('documentacion/', views.documentacion),
]