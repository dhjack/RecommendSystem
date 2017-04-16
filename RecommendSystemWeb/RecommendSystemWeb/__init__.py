#!/usr/bin/python
# -*- coding: utf-8 -*-  

from flask import Flask
import os

app = Flask(__name__)

import views

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', debug=True)
