#!/usr/bin/python
# -*- coding: utf-8 -*-

from RecommendSystemWeb import app
import os
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', debug=True)
