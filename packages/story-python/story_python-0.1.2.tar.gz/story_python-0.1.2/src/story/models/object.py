#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base


class Object(base.StoryBase):

    key = appier.field(index="hashed", safe=True, immutable=True)

    name = appier.field(index="hashed")

    engine = appier.field(index="hashed", safe=True, immutable=True)

    file = appier.field(type=appier.File, private=True)

    bucket = appier.field(type=appier.reference("Bucket", name="id"))

    @classmethod
    def validate(cls):
        return super(Object, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "key", "engine", "bucket"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    @appier.operation(
        name="Upload",
        parameters=(("Name", "name", str), ("File", "file", "file")),
        factory=True,
    )
    def upload_s(cls, name, file):
        file = appier.File(file)
        name = name or file.file_name
        object = cls(name=name, file=file)
        object.save()
        return object

    def pre_save(self):
        base.StoryBase.pre_save(self)
        if not hasattr(self, "engine") or not self.engine:
            self.engine = appier.conf("ENGINE", None)
        if hasattr(self, "key") and self.key:
            self.file.guid = self.key
        if hasattr(self, "engine") and self.engine:
            self.file.engine = self.engine

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
        self.file.guid = self.key

    def pre_delete(self):
        base.StoryBase.pre_delete(self)
        object = self.reload(rules=False)
        if object.file:
            object.file.delete()

    @appier.link(name="View")
    def view_url(self, absolute=False):
        return self.owner.url_for("object.data", key=self.key, absolute=absolute)

    @appier.link(name="Info")
    def info_url(self):
        return self.owner.url_for("object_api.info", key=self.key)

    @appier.link(name="Details")
    def details_url(self):
        return self.owner.url_for("object_api.details", key=self.key)

    @property
    def file_name(self):
        object = self.reload(rules=False)
        if object.name:
            return object.name
        return object.key
