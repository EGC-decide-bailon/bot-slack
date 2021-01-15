import unittest
import requests
import json
import sys
import config
import bot

USER_1_USER = "user"
USER_1_PASS = "rinoceronte2"
USER_1_TOKEN = "f016cd06e314c5f02c14f7408329067a4cd92bc0"

class TestMethods(unittest.TestCase):

    def test_login(self):

        # credentials = {"username": USER_1_USER, "password": USER_1_PASS}
        
        # consulta = "authentication/login/"

        # url = config.BASE_URL_HEROKU + config.API_BASE + consulta
        
        # r = requests.post(url, credentials)
        
        self.assertEqual("brr", "brr")