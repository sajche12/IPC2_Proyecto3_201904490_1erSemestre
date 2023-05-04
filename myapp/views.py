from django.shortcuts import render
from datetime import datetime
from .forms import CargarDatos, PruebaSolicitudes
from django.http import HttpResponse
from xml.etree import ElementTree as ET
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import FileResponse
import os


# Create your views here.
respuestas = {}
horas = list()
fechas = list()
respuestas["fechas"] = fechas
respuestas["horas"] = horas
usuarios = list()

def solicitar_servicio(request):
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M")
    if request.method == 'POST':
        form = CargarDatos(request.POST, request.FILES)
        if form.is_valid():
            global usuario
            usuario = form.cleaned_data['usuario']
            if usuario not in usuarios:
                usuarios.append(usuario)
            mensaje = form.cleaned_data['mensaje']
            archivo_xml = request.FILES.get('archivo')
            if archivo_xml and archivo_xml.name.endswith('.xml'):
                try:
                    tree = ET.parse(archivo_xml)
                    root = tree.getroot()
                    global diccionario
                    diccionario = {}  # Diccionario para guardar cada uno de los perfiles
                    global palabras_descartadas
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

            global resultados
            resultados = {}  # Diccionario para guardar los resultados
            for perfil, coincidencias in contador.items():
                resultados[perfil] = round(
                    (coincidencias / conteo_mensaje_construido)*100, 2)

            resultados_str = [
                f"{perfil}: {porcentaje}%" for perfil, porcentaje in resultados.items()]
            resultados_como_cadena = ", ".join(resultados_str)
            
            respuestas["horas"].append(hora_actual)
            respuestas["fechas"].append(fecha_actual)
            global zipped_list
            zipped_list = zip(respuestas['fechas'], respuestas['horas'])
            return HttpResponse(f"<h1>RESULTADOS:</h1><br>{resultados_como_cadena}")
    else:
        form = CargarDatos()
    return render(request, 'servicio.html', {'fecha': fecha_actual, 'hora': hora_actual, 'form': form})


def peticiones(request):
    return render(request, 'peticiones.html')

def ayuda(request):
    return render(request, 'ayuda.html')

def reset(request):
    respuestas.clear()
    horas.clear()
    fechas.clear()
    respuestas["fechas"] = fechas
    respuestas["horas"] = horas
    usuarios.clear()
    diccionario.clear()
    palabras_descartadas.clear()
    resultados.clear()
    return render(request, 'reset.html')

def detalles(request):
    return render(request, 'detalles.html', {'dic':diccionario, 'res':zipped_list, 'lista_usuarios':usuarios, 'resultados':resultados, 'usuario':usuario})

def resumen(request):
    return render(request, 'resumen.html', {'resultados':resultados, 'lista_usuarios':usuarios, 'usuario':usuario})

def solicitudes(request):
    form = PruebaSolicitudes()
    if request.method == 'POST':
        form = PruebaSolicitudes(request.FILES)
        if form.is_valid():
            archivo_xml = request.FILES.get('xml')
            if archivo_xml and archivo_xml.name.endswith('.xml'):
                try:
                    tree = ET.parse(archivo_xml)
                    root = tree.getroot()
                    palabras_clave = root.findall(".//text()[contains(., 'Guatemala')]")

                    fecha_hora = ""

                    if palabras_clave:
                        inicio = palabras_clave[0].find(":") + 2 # add 2 because ": " has 2 characters
                        fecha_hora = palabras_clave[0][inicio:]
                    print(fecha_hora)

                    
                except ET.ParseError:
                    return HttpResponse("Error al procesar el archivo XML")
                
    return render(request, 'solicitudes.html', {'form':form})

def exportar_detalles(request):
    context = {}
    html = render_to_string("detalles.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; detalles.pdf"    
    HTML(string=html).write_pdf(response)
    response['Content-Disposition'] = 'attachment; filename="detalles.pdf"'
    
    return response

def exportar_resumen(request):
    context = {}
    html = render_to_string("resumen.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; resumen.pdf"    
    HTML(string=html).write_pdf(response)
    response['Content-Disposition'] = 'attachment; filename="resumen.pdf"'
    
    return response

def informacion(request):
    nombre = "Diego Aldair Sajche Avila"
    carne = 201904490
    cui = 3011869790101
    link = "https://github.com/sajche12/IPC2_Proyecto3_201904490"
    return HttpResponse(f"<h2>Nombre: {nombre}</h2><br><h2>Carne: {carne}</h2><br><h2>CUI: {cui}</h2><br><h2>Link del repositorio: {link}</h2>")

def documentacion(request):
    #obtener la ruta completa del archivo
    full_path = os.path.join('Documentacion/Documentacion.pdf') 
    #Abrir el archivo en modo binario
    pdf = open(full_path, 'rb') 
    #retornar la respuesta del archivo pdf
    return FileResponse(pdf, content_type='application/pdf')