#!/usr/bin/python
# -*- coding: utf-8 -*-

class AuthManager:
    """
    Gestión de Autenticación y Cuentas. 
    Su única responsabilidad es validar quién es el usuario y crear nuevas cuentas de cliente.
    """
    def __init__(self):
        pass

    def login(self, email, password):
        """Valida las credenciales y devuelve el objeto Usuario si son correctas."""
        pass

    def registrarCliente(self, nombre, telefono, email, password):
        """Crea un nuevo Usuario y un Cliente asociado."""
        pass

    def usuarioLogueado(self, ):
        """Devuelve el usuario que está actualmente logueado."""
        pass
