#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

import appier


class BaseAPIController(appier.Controller):

    @appier.route("/api/ping", "GET", json=True)
    def ping(self):
        return dict(time=time.time())
