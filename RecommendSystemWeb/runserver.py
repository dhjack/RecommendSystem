#!/usr/bin/python
# -*- coding: utf-8 -*-


import Config
Config.init("./rs.conf")

from RecommendSystemWeb import app as application
application.secret_key = r'\xfb\xbb\x1a\xba\x94a?\xef\xba\x1c#\xf1JP\xf9V\x91\x14e\x8d\xa8\xa5\xc5\xcc'
application.run(host='0.0.0.0', debug=True)
