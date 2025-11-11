#!/usr/bin/python
# -*- coding: utf-8 -*-

from entidades.Usuario import Usuario


class Administrador(Usuario):
    def __init__(self):
        self.id_admin = None
        self.id_usuario = None
        self.nivel_acceso = None
