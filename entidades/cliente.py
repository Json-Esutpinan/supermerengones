#!/usr/bin/python
# -*- coding: utf-8 -*-

from entidades.Usuario import Usuario


class Cliente(Usuario):
    def __init__(self):
        self.id_cliente = None
        self.id_usuario = None
        self.nombre = None
        self.telefono = None
