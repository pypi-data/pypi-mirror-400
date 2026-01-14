#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier


class ObjectController(appier.Controller):

    @appier.route("/objects/<str:key>", "GET", json=True)
    @appier.route("/objects/<str:key>/data", "GET", json=True)
    def data(self, key):
        object_api = self.get_controller("ObjectAPIController")
        return object_api.data(key)
