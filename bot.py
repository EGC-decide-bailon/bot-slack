import slack
import os
import requests
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import config

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(config.SIGNING_SECRET, '/slack/events',app)

client = slack.WebClient(token=config.SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']

@app.route('/login-decide', methods=['POST'])
def login_decide():
    data = request.form
    text = data.get("text")
    informacion = text.split()
    user = informacion[0]
    clave = informacion[1]
    user_id = data.get('user_id')

    consulta = "authentication/login/"
    url = config.BASE_URL_HEROKU + config.API_BASE + consulta

    auth = {
        "username": str(user),
        "password": str(clave)
    }

    response = requests.post(url,auth)   
    data = response.json()
    token = data["token"]
    cadena = ""

    if(response.status_code==200):
        cadena = "Has iniciado sesión sin problema!"
    else:
        cadena = "Ha ocurrido un problema iniciando sesión"


    client.chat_postMessage(channel=user_id, text=cadena)
    return Response(), 200

@app.route('/info-comandos', methods=['POST'])
def info_comandos():
    data = request.form
    user_id = data.get('user_id')
    client.chat_postMessage(channel=user_id, text="Buenas! a continuación te dejaré los comandos disponibles para realizar la votación en decide")
    client.chat_postMessage(channel=user_id, text="/login-decide -> Te perminte iniciar sesión en decide, introduce el comando /login-decide [usuario] [contraseña]")

    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)