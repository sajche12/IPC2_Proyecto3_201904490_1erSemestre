from django.shortcuts import render
from datetime import datetime
from .forms import CargarXml

# Create your views here.


def solicitar_servicio(request):
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M")
    return render(request, 'servicio.html', {'fecha':fecha_actual, 'hora':hora_actual, 'form':CargarXml})

def peticiones(request):
    return render(request, 'peticiones.html')

def ayuda(request):
    return render(request, 'ayuda.html')

def reset(request):
    return render(request, 'reset.html')
