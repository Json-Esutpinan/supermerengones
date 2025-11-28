#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuración de fixtures para pytest
"""

import pytest
import bcrypt
from django.contrib.auth import get_user_model
from entidades.usuario import Usuario
from entidades.cliente import Cliente
from entidades.empleado import Empleado
from entidades.administrador import Administrador
from entidades.sede import Sede
from entidades.producto import Producto
from entidades.pedido import Pedido
from dao.usuarioDAO import UsuarioDAO
from dao.clienteDAO import ClienteDAO
from dao.empleadoDAO import EmpleadoDAO
from dao.administradorDAO import AdministradorDAO
from dao.sedeDAO import SedeDAO
from dao.productoDAO import ProductoDAO
from dao.pedidoDAO import PedidoDAO
from dao.turnoDAO import TurnoDAO
from datetime import date, time, datetime


@pytest.fixture
def sede_test():
    """Crea una sede de prueba"""
    sede_dao = SedeDAO()
    sede = Sede(
        nombre="Sede Test",
        direccion="Av. Test 123",
        telefono="999999999",
        activo=True
    )
    resp = sede_dao.crear(sede)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def usuario_cliente_test():
    """Crea un usuario cliente de prueba"""
    usuario_dao = UsuarioDAO()
    # Hashear password usando bcrypt
    password_hash = bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode()
    usuario = Usuario(
        nombre="Cliente Test",
        email=f"cliente_test_{datetime.now().timestamp()}@test.com",
        password=password_hash,
        rol="cliente",
        activo=True
    )
    resp = usuario_dao.crear(usuario)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def cliente_test(usuario_cliente_test):
    """Crea un cliente de prueba"""
    if not usuario_cliente_test:
        return None
    
    cliente_dao = ClienteDAO()
    cliente = Cliente(
        id_usuario=usuario_cliente_test['id_usuario'],
        telefono="999888777",
        direccion="Calle Test 456"
    )
    resp = cliente_dao.crear(cliente)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def usuario_empleado_test():
    """Crea un usuario empleado de prueba"""
    usuario_dao = UsuarioDAO()
    password_hash = bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode()
    usuario = Usuario(
        nombre="Empleado Test",
        email=f"empleado_test_{datetime.now().timestamp()}@test.com",
        password=password_hash,
        rol="empleado",
        activo=True
    )
    resp = usuario_dao.crear(usuario)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def empleado_test(usuario_empleado_test, sede_test):
    """Crea un empleado de prueba"""
    if not usuario_empleado_test or not sede_test:
        return None
    
    empleado_dao = EmpleadoDAO()
    empleado = Empleado(
        id_usuario=usuario_empleado_test['id_usuario'],
        id_sede=sede_test['id_sede'],
        cargo="Cajero",
        fecha_ingreso=date.today()
    )
    resp = empleado_dao.crear(empleado)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def usuario_admin_test():
    """Crea un usuario administrador de prueba"""
    usuario_dao = UsuarioDAO()
    password_hash = bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode()
    usuario = Usuario(
        nombre="Admin Test",
        email=f"admin_test_{datetime.now().timestamp()}@test.com",
        password=password_hash,
        rol="administrador",
        activo=True
    )
    resp = usuario_dao.crear(usuario)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def admin_test(usuario_admin_test):
    """Crea un administrador de prueba"""
    if not usuario_admin_test:
        return None
    
    admin_dao = AdministradorDAO()
    admin = Administrador(
        id_usuario=usuario_admin_test['id_usuario'],
        nivel_acceso="total"
    )
    resp = admin_dao.crear(admin)
    if resp.data:
        return resp.data[0]
    return None


@pytest.fixture
def producto_test():
    """Crea un producto de prueba"""
    producto_dao = ProductoDAO()
    producto = Producto(
        codigo=f"PROD-TEST-{datetime.now().timestamp()}",
        nombre="Producto Test",
        descripcion="Descripción de prueba",
        id_unidad=1,  # Asumiendo que existe una unidad con id 1
        contenido=500,  # Contenido numérico (500 gramos)
        precio=50.00,
        stock=100,
        activo=True
    )
    resp = producto_dao.insertar(producto)  # ProductoDAO usa insertar(), no crear()
    if resp:  # insertar() devuelve Producto o None, no response
        return resp.to_dict()
    return None


@pytest.fixture
def turno_test(empleado_test, sede_test):
    """Crea un turno de prueba"""
    if not empleado_test or not sede_test:
        return None
    
    turno_dao = TurnoDAO()
    from entidades.turno import Turno
    
    turno = Turno(
        id_empleado=empleado_test['id_empleado'],
        fecha=date.today(),
        hora_inicio=time(8, 0),
        hora_fin=time(16, 0)
    )
    resp = turno_dao.crear(turno)
    if resp.data:
        return resp.data[0]
    return None
