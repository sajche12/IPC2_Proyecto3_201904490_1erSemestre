from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def hello():
    return Response({'message': 'Hello World!'})

@app.route('/servicio/', methods=['POST'])
def servicio(request):
    print(request.method)
    return Response(request.data)

if __name__ == '__main__':
    app.run(debug=True)
