import slack
import os
import requests
from flask import Flask, request, Response
from requests.auth import HTTPBasicAuth
import json
import config

#Creación de la aplicación web con flask 
app = Flask(__name__)

client = slack.WebClient(token=config.SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']

DIC = {}

# Este comando muestra información con los comandos disponibles para realizar la votación en decide, así como las intrucciones con los datos necesarios.
@app.route('/info-comandos', methods=['POST'])
def info_comandos():
    data = request.form
    user_id = data.get('user_id')
    client.chat_postMessage(channel=user_id, text="Buenas! a continuación te dejaré los comandos disponibles para realizar la votación en decide. Recuerde que es necesario logearse antes de utilizar los demás comandos")
    client.chat_postMessage(channel=user_id, text="/login-decide -> Te permite iniciar sesión en decide, introduce el comando /login-decide [usuario] [contraseña]")
    client.chat_postMessage(channel=user_id, text="/votaciones-disponibles -> Te perminte ver las votaciones disponibles actualmente en decide, introduce el comando /votaciones-disponibles")
    client.chat_postMessage(channel=user_id, text="/detalles-votacion -> Te perminte ver información sobre la encuesta elegida, introduce el comando /detalles-votacion [idVotación]")
    client.chat_postMessage(channel=user_id, text="/votar-decide -> Te perminte realizar una votación para la encuesta solicitada, introduce el comando /votar-decide [idVotación] [respuesta]")

    return Response(), 200

# Este comando te permite recoger la información que se le pasa como parámetro en slack y realiza el inicio de sesión guardando el token recibido.
@app.route('/login-decide', methods=['POST'])
def login_decide():
    data = request.form
    text = data.get("text")
    informacion = text.split()
    user = informacion[0]
    clave = informacion[1]
    user_id = data.get('user_id')

    url = config.BASE_URL_HEROKU + config.API_BASE + "authentication/login/"

    auth = {
        "username": str(user),
        "password": str(clave)
    }

    #Comprobamos con la expección que ha podido loguearse correctamente
    try:
        response = requests.post(url,auth)
        data = response.json()
        token = data["token"]
        DIC[str(user_id)] = token
    except:
        client.chat_postMessage(channel=user_id, text="El usuario o contraseña introducidos no son correctos")

    if(response.status_code==200):
        client.chat_postMessage(channel=user_id, text="Has iniciado sesión correctamente")

    return Response(), 200

# Este comando permite ver las votaciones disponibles en decide
@app.route('/votaciones-disponibles', methods=['POST'])
def votaciones_disponibles():
    data = request.form
    user_id = data.get('user_id')

    #Se hace un try/catch para controlar la posible excepción que saltará si se intenta ver las votaciones sin haber iniciado sesión previamente
    try:
        token = DIC[str(user_id)]
        headers = {"token": str(token)}
        url = config.BASE_URL_HEROKU + config.API_BASE + "voting/"
        response = requests.get(url, headers = headers)
        response = json.loads(response.text)
        votacionesDisponibles  = cogerVotaciones(response)

        numeroVotaciones = len(votacionesDisponibles)

        listaCadenas=[]
        for e in votacionesDisponibles:
            cadena = "id de la votación - "+ str(e.get("id")) + " - Título: "+str(e.get("name"))+" - Descripción: "+ str(e.get("question").get("desc"))
            listaCadenas.append(cadena)

        cadena = "Actualmente hay "+str(numeroVotaciones)+" encuestas disponibles. Para acceder a una votación particular debes utilizar el comando /detalles-votacion [id]"

        for c in listaCadenas:
            cadena = cadena + "\n"+c

        client.chat_postMessage(channel=user_id, text=cadena)
    except :
        client.chat_postMessage(channel=user_id, text="Para poder ver las encuestas disponibles, debes iniciar sesión primero")

    return Response(), 200

def cogerVotaciones(response):
    listaAux = []
    for r in response:
        v = {'id': r['id'], 'name': r['name'], 'desc': r['desc'], 'end_date': r['end_date'],
             'start_date': r['start_date'], 'question': r['question'], 'pub_key': r['pub_key']}

        if v['start_date'] is not None and v['end_date'] is None:
            listaAux.append(v)

    return listaAux

# Este comando permite ver una votación especifica a partir de la id que se le pasa
@app.route('/detalles-votacion', methods=['POST'])
def detalles_votacion():
    data = request.form
    user_id = data.get('user_id')
    idVotacion = data.get("text")  
    url_base = config.BASE_URL_HEROKU + config.API_BASE
    url = url_base + "voting/?id=" + str(idVotacion)

    try:
        token = DIC[str(user_id)]
        headers = {"token": str(token)}
        try:
            response = requests.get(url, headers = headers)
            r = json.loads(response.text)
            r = r[int(idVotacion)-1]

            v = {'id': r['id'], 'name': r['name'], 'desc': r['desc'], 'end_date': r['end_date'],'start_date': r['start_date'], 'question': r['question'], 'pub_key': r['pub_key']}
            options = v["question"].get("options")

            opt1 = options[0]
            opt2 = options[1]

            client.chat_postMessage(channel=user_id, text="Título: "+ str(v["name"])+ ", id de la votación: "+str(v["id"])+". Opcione de votación:\n" + "Opción "+ str(opt1.get("number"))+" equivale a "+str(opt1.get("option"))+ "\nOpción "+ str(opt2.get("number"))+" equivale a "+str(opt2.get("option")))
            client.chat_postMessage(channel=user_id, text="Recuerda que para realizar la votación, debes utilizar el comando /votar-decide [id] [respuesta]")
        except:
            client.chat_postMessage(channel=user_id, text="El id introducido no coincide con ninguna votación")

    except:
        client.chat_postMessage(channel=user_id, text="Para poder ver las encuestas solicitada, debes iniciar sesión primero")

    return Response(), 200

# Este comando permite realizar la votación para la encuesta elegida con el valor elegido
@app.route('/votar-decide', methods=['POST'])
def votar_decide():
    data = request.form
    user_id = data.get('user_id')
    text = data.get("text")
    informacion = text.split()
    encuesta = informacion[0]
    respuesta = informacion[1]

    try:
        token = DIC[str(user_id)]
        token = str(token)
        user = get_user(token)
        user = json.loads(user.text)
        user_decide_id= user['id']

        try:
            a,b = 0,0
            if int(respuesta) == 1:
                a = 1
            elif int(respuesta) == 2:
                b = 1
            else:
                client.chat_postMessage(channel=user_id, text="La respuesta introducida no es válida")

            data_dict = {
                "vote": { "a": a,"b":b},
                "voting": encuesta,
                "voter": user_decide_id,
                "token": token
            }
            save_vote_data(data_dict,token)

            if a != 0 or b != 0:
                client.chat_postMessage(channel=user_id, text="Se ha realizado la votación correctamente")
        except:
            client.chat_postMessage(channel=user_id, text="El id de la votación o la respuesta introducida son incorrectos")
    except:
        client.chat_postMessage(channel=user_id, text="Para poder realizar la encuesta solicitada, debes iniciar sesión primero")

    return Response(), 200

# Se pasa el token como parámetro y se hace una petición a la API para recibir la información del usuario 
def get_user(token):

    data = {'token': token}
    usuario = requests.post(config.BASE_URL_HEROKU + "authentication/getuser/", data)

    return usuario

# Se pasa el token y los datos de la votación como parámetros para realizar la votación
def save_vote_data(data_dict,token):
   
    headers = {"Authorization": "Token " + token,
                "Content-Type": "application/json"}
    
    r = requests.post(config.BASE_URL_HEROKU + "store/", json=data_dict, headers = headers)

    return r


if __name__ == "__main__":
    app.run(debug=True)