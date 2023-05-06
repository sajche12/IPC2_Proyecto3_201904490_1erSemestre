from flask import Flask, request, Response
from funciones.procesos import archivo_mensajes, archivo_perfiles, procedimiento
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return Response({'message': 'Hello World!'})

@app.route('/carga1', methods=['POST'])
def carga1():
    if request.method=='POST':
        if 'ArchivoPalabras1' in request.files:
            archivo = request.files['ArchivoPalabras1']
            return Response(archivo_perfiles(archivo), status=201, mimetype='text/xml')
        else:
            return "Falta el campo de formulario 'ArchivoPalabras1' en la solicitud"
    else:
        return '<h2>¡Se ha producido un error! :(</h2>'

@app.route('/carga2', methods=['POST'])
def carga2():
    if request.method=='POST':
        if 'mensajes' in request.files:
            archivo = request.files['mensajes']
            return Response(archivo_mensajes(archivo), status=201, mimetype='text/xml')
        else:
            return "Falta el campo de formulario 'mensajes' en la solicitud"

@app.route('/procesar_xml', methods=['POST'])
def procesar_xml():
    perfiles = request.files['perfiles']
    mensajes = request.files['mensajes']
    # Aquí puedes procesar los archivos XML como desees
    resultado = procedimiento(perfiles, mensajes)
    return resultado
    
@app.route('/procesar_xml', methods=['POST'])
def solicitudes():
    if request.method=='POST':
        #return Response(ProcessData(request.data),status=201, mimetype='text/xml')
        pass

if __name__ == '__main__':
    app.run(debug=True)
