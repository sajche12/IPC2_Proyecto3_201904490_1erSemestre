from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import FileResponse
import os, re, chardet
from datetime import datetime
from xml.etree import ElementTree as ET
from .forms import CargarDatos, PruebaSolicitudes

# Create your views here.
diccionario = {}   # Diccionario para guardar todos los datos
diccionario['fechas_horas'] = []
diccionario['usuarios'] = []
diccionario['palabras_descartadas'] = []


def solicitar_servicio(request):
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M")
    if request.method == 'POST':
        form = CargarDatos(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            if usuario not in diccionario['usuarios']:
                diccionario['usuarios'].append(usuario)
            mensaje = form.cleaned_data['mensaje']
            # if mensaje is None:
            # mensaje = mensaje_entrada
            archivo_xml = request.FILES.get('archivo')
            if archivo_xml and archivo_xml.name.endswith('.xml'):
                try:
                    tree = ET.parse(archivo_xml)
                    root = tree.getroot()

                    global perfiles
                    perfiles = {}   # Diccionario para guardar los perfiles
                    for perfil in root.findall('./perfiles/perfil'):
                        nombre_perfil = perfil.find('nombre').text
                        perfiles[nombre_perfil] = []

                    for perfil in root.findall('./perfiles/perfil'):
                        nombre_perfil = perfil.find('nombre').text
                        lista_palabras = []
                        palabras = perfil.find('palabrasClave')
                        for palabra in palabras.findall('palabra'):
                            lista_palabras.append(palabra.text)
                        perfiles[nombre_perfil] = lista_palabras

                    for descartada in root.findall('./descartadas'):
                        for i in descartada.findall('palabra'):
                            diccionario['palabras_descartadas'].append(i.text)

                    # Agrega otras variables aquí según los campos del formulario
                except ET.ParseError:
                    return HttpResponse("Error al procesar el archivo XML")
            else:
                return HttpResponse("El archivo enviado no es válido o no es un archivo XML")

            mensaje_nuevo = mensaje.split()
            for palabra_descartada in diccionario['palabras_descartadas']:
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

            for perfil, lista_palabras in perfiles.items():
                coincidencias = 0
                for palabra in lista_palabras:
                    if palabra.lower() in mensaje.lower():
                        coincidencias += 1
                # contador ahora guarda el número de coincidencias en cada lista de palabras clave para cada perfil en diccionario
                contador[perfil] = coincidencias

            conteo_palabras = {}
            for perfil, palabras in perfiles.items():
                conteo_palabras[perfil] = len(palabras)

            # Crear una lista para cada nombre de perfil
            perfiles_lista = []
            for perfil in contador:
                perfiles_lista.append(perfil)

            # Inicializar un diccionario vacío para almacenar las listas de porcentajes de cada perfil
            global resultados
            resultados = {perfil: [] for perfil in perfiles_lista}

            # Verificar si el diccionario ya ha sido inicializado
            if 'resultados' not in globals():
                # Inicializar un diccionario vacío para almacenar las listas de porcentajes de cada perfil
                resultados = {perfil: [] for perfil in perfiles_lista}

            # Actualizar el diccionario 'resultados' con los porcentajes de coincidencia
            for perfil in perfiles_lista:
                porcentaje = round(
                    (contador[perfil] / conteo_mensaje_construido) * 100, 2)
                resultados[perfil].append(porcentaje)

            # Crear una lista de strings con la información de 'resultados'
            resultados_str = [
                f"{perfil}: {resultados[perfil]}%" for perfil in resultados.keys()]
            resultados_como_cadena = ", ".join(resultados_str)

            diccionario['fechas_horas'].append(f"{fecha_actual} {hora_actual}")

            return HttpResponse(f"<h1>RESULTADOS:</h1><br><h2>{resultados_como_cadena}</h2>")
    else:
        form = CargarDatos()
    return render(request, 'servicio.html', {'fecha': fecha_actual, 'hora': hora_actual, 'form': form})


def peticiones(request):
    return render(request, 'peticiones.html')


def ayuda(request):
    return render(request, 'ayuda.html')


def reset(request):
    diccionario.clear()
    diccionario['fechas_horas'] = []
    diccionario['usuarios'] = []
    diccionario['palabras_descartadas'] = []
    resultados.clear()
    return render(request, 'reset.html')


def detalles(request):
    fecha = request.GET.get('fecha')
    usuario = request.GET.get('usuario')  # el usuario debe ser tomado del POST
    return render(request, 'detalles.html', {'dic': diccionario, 'resultados': resultados, 'perfiles': perfiles, 'usuario_selec': usuario})


def resumen(request):
    pass
    return render(request, 'resumen.html', {'dic': diccionario, 'resultados': resultados})

def solicitudes(request):
    mensajes = {}
    mensajes['fecha_hora'] = []
    mensajes['usuario'] = []
    mensajes['mensaje'] = []
    form = PruebaSolicitudes()
    if request.method == 'POST':
        form = PruebaSolicitudes(request.POST, request.FILES)
        archivo_xml = request.FILES.get('archivo')
        if archivo_xml is not None and archivo_xml.name.endswith('.xml'):  
            try:           
                tree = ET.parse(archivo_xml)
                root = tree.getroot()
                
                for mensaje in root.findall("./mensaje"):
                    texto_mensaje = mensaje.text
                    resultado1 = re.search(r'Guatemala,([\s\S]*)Usuario', texto_mensaje)
                    resultado2 = re.search(r'Usuario:\s(.*)\sRed', texto_mensaje)
                    resultado3 = re.search(r'ChapinChat\s(.*)', texto_mensaje, re.UNICODE)
                    
                    if resultado1:
                        fecha_hora = resultado1.group(1).strip()
                        mensajes['fecha_hora'].append(fecha_hora)
                    if resultado2:
                        usuario_actual = resultado2.group(1).strip()
                        if 'usuario' in mensajes:
                            mensajes['usuario'].append(usuario_actual)
                        else:
                            mensajes['usuario'] = [usuario_actual]
                    if resultado3:
                        mensaje = resultado3.group(1).strip()
                        mensajes['mensaje'].append(mensaje)
                        
            except ET.ParseError:
                return HttpResponse("Error al procesar el archivo XML") 
        return JsonResponse({'mensajes': mensajes})


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
    # obtener la ruta completa del archivo
    full_path = os.path.join('Documentacion/Documentacion.pdf')
    # Abrir el archivo en modo binario
    pdf = open(full_path, 'rb')
    # retornar la respuesta del archivo pdf
    return FileResponse(pdf, content_type='application/pdf')
