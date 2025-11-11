#!/usr/bin/python
# -*- coding: utf-8 -*-

from entidades.Usuario import Usuario


class Empleado(Usuario):
    def __init__(self):
        self.id_empleado = None
        self.id_usuario = None
        self.id_sede = None
        self.id_turno = None
        self.cargo = None
        self.fecha_ingreso = None
