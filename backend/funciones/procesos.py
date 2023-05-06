from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
import re, string, os

perfiles = {}   # Diccionario para guardar los perfiles y palabras descartdas
perfiles['palabras_descartadas'] = []
mensajes = {}   #Diccionario para guardar los mensajes
mensajes['fecha_hora'] = []
mensajes['usuario'] = []
mensajes['mensaje'] = []

def extraccion_perfiles(xml):
    if xml:
        try:
            try:
                with open(xml, 'r') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
            except FileNotFoundError:
                print("ERROR: File not found")
                return {}
        except ET.ParseError:
            print("ERROR AL PARSEAR PERFILES")
        
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
                perfiles['palabras_descartadas'].append(i.text)
    print(perfiles)
    return perfiles

def extraccion_mensajes(xml):
    
    if os.path.isfile(xml):
        if xml:
            try:
                root=ET.fromstring(xml)
                
            except ET.ParseError:
                print("ERROR AL PARSEAR MENSAJES")
            
            for mensaje in root.findall("./mensaje"):
                texto_mensaje = mensaje.text
                resultado1 = re.search(r'Guatemala,([\s\S]*)Usuario', texto_mensaje)
                resultado2 = re.search(r'Usuario:\s(.*)\sRed', texto_mensaje)
                resultado3 = re.search(r'ChapinChat\s(.*)', texto_mensaje)
            
                if resultado1:
                    fecha_hora = resultado1.group(1).strip()
                    mensajes['fecha_hora'].append(fecha_hora)
                if resultado2:
                    usuario = resultado2.group(1).strip()
                    mensajes['usuario'].append(usuario)
                if resultado3:
                    mensaje = resultado3.group(1).strip()
                    mensajes['mensaje'].append(mensaje)
        print(mensajes)
        return mensajes
    else:
        
        print("ARCHIVO NO ENCONTRADO")

def remover_numeros(s):
    # Comprobar si la cadena contiene un carácter numérico o puntuación
    if any(char.isdigit() or char in string.punctuation for char in s):
        # Eliminar caracteres numéricos y puntuación de la cadena
        s = ''.join(char for char in s if not (char.isdigit() or char in string.punctuation))
    return s

def procedimiento(xml_file_1, xml_file_2):
    
    contenido_1 = xml_file_1.read().decode('utf-8')
    contenido_2 = xml_file_2.read().decode('utf-8')
    
    perfiles = extraccion_perfiles(contenido_1)
    mensajes = extraccion_mensajes(contenido_2)
    
    perfiles_filt = {k: v for k, v in perfiles.items() if k != 'palabras_descartadas'}
    resultados = {}
    for nombre_lista in perfiles_filt:
        resultados[nombre_lista] = {}
    for mensaje in mensajes.values():
        # Elimina los caracteres numéricos y de puntuación del mensaje  
        mensaje['mensaje'] = remover_numeros(mensaje['mensaje'])
        palabras_mensaje = mensaje['mensaje'].split()
        for palabra in palabras_mensaje:
            if palabra in perfiles['palabras_descartadas']:
                palabras_mensaje.remove(palabra)
        for nombre_lista, lista in perfiles_filt.items():
            palabras_coincidentes = list(set(palabras_mensaje) & set(lista))
            division = len(palabras_coincidentes) / len(palabras_mensaje)
            resultados[nombre_lista][mensaje['id_mensaje']] = division

def archivo_perfiles(xml):
    global archivo_p
    archivo_p = xml
    return archivo_p
    
def archivo_mensajes(xml):
    global archivo_p
    archivo_m = xml
    procedimiento(archivo_p, archivo_m)

def construccion_xml(dic):
    # obtenemos los valores requeridos
    #fecha_hora = diccionario.get('fecha_hora')
    #usuario = diccionario.get('usuario')

    
    # Creamos el elemento root y los elementos necesarios
    root = ET.Element('respuesta')
    fecha_hora_element = ET.SubElement(root, "fechaHora")
    usuario_element = ET.SubElement(root, "usuario")
    perfiles_element = ET.SubElement(root, "perfiles")
    perfil_element = ET.SubElement(perfiles_element, "perfil")
    nombre_element = ET.SubElement(perfil_element, "nombre")
    probabilidad_element = ET.SubElement(perfil_element, "porcentajeProbabilidad")
    peso_actual_element = ET.SubElement(perfil_element, "pesoActual")

    # Agregamos los valores obtenidos como contenido de los elementos correspondientes
    #fecha_hora_element.text = fecha_hora
    #usuario_element.text = usuario
    # nombre_element.text = nombre
    # probabilidad_element.text = probabilidad
    # peso_actual_element.text = peso_actual

    # Creamos y guardamos el archivo XML
    tree = ET.ElementTree(root)
    tree.write("respuesta.xml")
