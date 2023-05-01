from django.shortcuts import render
from datetime import datetime
from .forms import CargarDatos
from django.http import HttpResponse
from xml.etree import ElementTree as ET

# Create your views here.
diccionario = {}  # Diccionario para guardar cada uno de los perfiles
resultados = {}  # Diccionario para guardar los resultados


def solicitar_servicio(request):
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M")
    if request.method == 'POST':
        form = CargarDatos(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            mensaje = form.cleaned_data['mensaje']
            archivo_xml = request.FILES.get('archivo')
            if archivo_xml and archivo_xml.name.endswith('.xml'):
                try:
                    tree = ET.parse(archivo_xml)
                    root = tree.getroot()

                    palabras_descartadas = []  # Lista para las palabras descartadas

                    for perfil in root.findall('./perfiles/perfil'):
                        nombre_perfil = perfil.find('nombre').text
                        diccionario[nombre_perfil] = []

                    for perfil in root.findall('./perfiles/perfil'):
                        nombre_perfil = perfil.find('nombre').text
                        lista_palabras = []
                        palabras = perfil.find('palabrasClave')
                        for palabra in palabras.findall('palabra'):
                            lista_palabras.append(palabra.text)
                        diccionario[nombre_perfil] = lista_palabras

                    for descartada in root.findall('./descartadas'):
                        for i in descartada.findall('palabra'):
                            palabras_descartadas.append(i.text)

                    # Agrega otras variables aquí según los campos del formulario
                except ET.ParseError:
                    return HttpResponse("Error al procesar el archivo XML")
            else:
                return HttpResponse("El archivo enviado no es válido o no es un archivo XML")

            mensaje_nuevo = mensaje.split()
            for palabra_descartada in palabras_descartadas:
                for palabra in mensaje_nuevo:
                    if palabra.lower() == palabra_descartada.lower():
                        mensaje_nuevo.remove(palabra)
            palabras_sin_numeros = []
            for palabra in mensaje_nuevo:
                if not palabra.isdigit():
                    palabras_sin_numeros.append(palabra)

             # Reconstruir mensaje sin las palabras descartadas
            mensaje_construido = ' '.join(palabras_sin_numeros)
            conteo_mensaje_construido = len(mensaje_construido.split())

            contador = {}  # Diccionario para guardar el contador de coincidencias por perfil

            for perfil, lista_palabras in diccionario.items():
                coincidencias = 0
                for palabra in lista_palabras:
                    if palabra.lower() in mensaje.lower():
                        coincidencias += 1
                # contador ahora guarda el número de coincidencias en cada lista de palabras clave para cada perfil en diccionario
                contador[perfil] = coincidencias

            conteo_palabras = {}
            for perfil, palabras in diccionario.items():
                conteo_palabras[perfil] = len(palabras)

            for perfil, coincidencias in contador.items():
                resultados[perfil] = round(
                    (coincidencias / conteo_mensaje_construido)*100, 2)

    else:
        form = CargarDatos()
    return render(request, 'servicio.html', {'fecha': fecha_actual, 'hora': hora_actual, 'form': form})


def peticiones(request):
    return render(request, 'peticiones.html')


def ayuda(request):
    return render(request, 'ayuda.html')


def reset(request):
    return render(request, 'reset.html')

def resultado(request):
    return render(request, 'resultados.html', {'res':resultados})