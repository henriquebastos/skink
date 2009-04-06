#!/usr/bin/env python
#-*- coding:utf-8 -*-
from elixir import *

class ModelHelper(object):
    @classmethod
    def assert_not_empty(self, message, **arguments):
        return_message = []
        for argument, value in arguments.items():
            if value is None or value == "":
                return_message.append(message % argument)
        if return_message:
            raise ValueError("The following errors happened:\n%s" % "\n".join(return_message))

class Project (Entity):
    name = Field(Unicode(255))
    build_script = Field(Unicode(2000))
    scm_repository = Field(Unicode(1500))
    
    def __init__(self, name, build_script, scm_repository):
        ModelHelper.assert_not_empty("The field %s of the Project model must not be empty or null.", name=name, build_script=build_script, scm_repository=scm_repository)
        self.name = name
        self.build_script = build_script
        self.scm_repository = scm_repository
        