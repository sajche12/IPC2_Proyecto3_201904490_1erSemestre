from django.urls import path
from . import views

urlpatterns = [
    path('servicio/', views.solicitar_servicio),
    path('peticiones/', views.peticiones),
    path('ayuda/', views.ayuda),
    path('reset/', views.reset),
    path('resultados/', views.resultados),
]