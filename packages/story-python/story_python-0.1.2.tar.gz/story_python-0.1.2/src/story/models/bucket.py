#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base


class Bucket(base.StoryBase):

    key = appier.field(index="hashed", safe=True, immutable=True)

    name = appier.field(index="hashed")

    @classmethod
    def validate(cls):
        return super(Bucket, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "key"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
