import unittest
import requests
import json
import sys
import config
URL_BASE = 'https://decide-voting.herokuapp.com/'
URL_GW = URL_BASE + 'gateway/'
DIC = {}


class TestMethods(unittest.TestCase):

    #Probamos si inicia sesión bien con las credenciales correctas
    def test_1login_valido(self):
        datos = {"username": "user", "password":"rinoceronte2"}
        r = requests.post(config.BASE_URL_HEROKU + config.API_BASE + "authentication/login/",datos)
        data = r.json()
        DIC["token"] = data["token"]
        self.assertEqual(r.status_code,200)

    #Probamos si falla al iniciar sesión con las credenciales incorrectas
    def test_login_error(self):
        datos = {"username": "pruebaMal", "password":"pruebaMal"}
        r = requests.post(config.BASE_URL_HEROKU + config.API_BASE + "authentication/login/",datos)
        self.assertEqual(r.status_code,400)

    #Probamos si puedes acceder a las votaciones de decide
    def test_votaciones_disponibles(self):
        datos = {}
        r = requests.get(config.BASE_URL_HEROKU + config.API_BASE + "voting/",datos)
        self.assertEqual(r.status_code,200)

    def test_detalles_votacion_valido(self):
        datos = {}
        idVotacion = "1"
        aux = requests.get(config.BASE_URL_HEROKU + config.API_BASE + "voting/?id=" + idVotacion,datos)
        r = json.loads(aux.text)
        r = r[int(idVotacion)-1]
        v = {'id': r['id'], 'name': r['name'], 'desc': r['desc'], 'end_date': r['end_date'],'start_date': r['start_date'], 'question': r['question'], 'pub_key': r['pub_key']}
        self.assertEqual(int(idVotacion), v["id"])

    def test_detalles_votacion_error(self):
        datos = {}
        idVotacion = 190
        is_done =  True
        aux = requests.get(config.BASE_URL_HEROKU + config.API_BASE + "voting/?id=" + str(idVotacion),datos)
        r = json.loads(aux.text)
        try:
            r = r[idVotacion-1]
        except:
            is_done = False
        self.assertFalse(is_done)

    def test_usuario(self):
        token = DIC["token"]
        datos = {'token': token}
        r = requests.post(config.BASE_URL_HEROKU + "authentication/getuser/",datos)
        self.assertEqual(r.status_code,200)    

    def test_votar_valido(self):
        token = DIC["token"]
        datos = {"Authorization": "Token " + token,
                "Content-Type": "application/json"}
        data_dict = {
            "vote": { "a": 1,"b":0},
            "voting": 1,
            "voter": 2,
            "token": token
        }

        aux = requests.post(config.BASE_URL_HEROKU + "store/", json=data_dict, headers = datos)

        self.assertEqual(aux.status_code,200)

    
if __name__ == '__main__':
    unittest.main()