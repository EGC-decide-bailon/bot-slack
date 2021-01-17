import unittest
import requests
import json
import sys
import config
URL_BASE = 'https://decide-voting.herokuapp.com/'
URL_GW = URL_BASE + 'gateway/'

class TestMethods(unittest.TestCase):

    def login_test_valido(self):
        datos = {"username": "user", "password":"rinoceronte2"}
        r = requests.post(URL_GW + 'authentication/login' + datos)
        self.assertEqual(r.status_code,200)

    def login_test_error(self):
        datos = {"username": "pruebaMal", "password":"pruebaMal"}
        r = requests.post(URL_GW + 'authentication/login' + datos)
        self.assertEqual(r.status_code,401)

if __name__ == '__main__':
    unittest.main()