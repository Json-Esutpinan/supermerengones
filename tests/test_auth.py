#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para Autenticación y Registro
Tests para AuthManager
"""

import pytest
from datetime import datetime
from manager.authManager import AuthManager
from dao.usuarioDAO import UsuarioDAO
from dao.clienteDAO import ClienteDAO
from entidades.usuario import Usuario
from entidades.cliente import Cliente


class TestAuthManager:
    """Tests para el gestor de autenticación"""
    
    @pytest.mark.database
    def test_registrar_cliente_exitoso(self):
        """Test: Registrar nuevo cliente correctamente"""
        manager = AuthManager()
        
        email = f"nuevo_cliente_{datetime.now().timestamp()}@test.com"
        resultado = manager.registrarCliente(
            nombre="Juan Pérez",
            telefono="987654321",
            email=email,
            direccion="Av. Test 123",
            password="password123"
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert 'data' in resultado
        assert resultado['data']['usuario'].email == email
        assert resultado['data']['usuario'].rol == 'cliente'
    
    @pytest.mark.database
    def test_registrar_cliente_email_duplicado(self):
        """Test: No permite registrar con email duplicado"""
        manager = AuthManager()
        
        email = f"duplicado_{datetime.now().timestamp()}@test.com"
        
        # Primer registro
        resultado1 = manager.registrarCliente(
            nombre="Usuario 1",
            telefono="111111111",
            email=email,
            direccion="Dir 1",
            password="pass123456"
        )
        # Asegurarse que el primer registro fue exitoso
        if not resultado1['success']:
            pytest.fail(f"Primer registro falló: {resultado1['message']}")
        
        # Segundo registro con mismo email (debe fallar)
        resultado2 = manager.registrarCliente(
            nombre="Usuario 2",
            telefono="222222222",
            email=email,
            direccion="Dir 2",
            password="pass654321"
        )
        assert resultado2['success'] is False
        assert "ya está registrado" in resultado2['message']
    
    @pytest.mark.database
    def test_login_exitoso(self, usuario_cliente_test):
        """Test: Login con credenciales correctas"""
        if not usuario_cliente_test:
            pytest.skip("No se pudo crear usuario de prueba")
        
        manager = AuthManager()
        
        resultado = manager.login(
            email=usuario_cliente_test['email'],
            password="test123"  # Password del fixture
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert resultado['data']['usuario'].email == usuario_cliente_test['email']
        assert resultado['data']['rol'] == 'cliente'
    
    @pytest.mark.database
    def test_login_password_incorrecto(self, usuario_cliente_test):
        """Test: Login con password incorrecto falla"""
        if not usuario_cliente_test:
            pytest.skip("No se pudo crear usuario de prueba")
        
        manager = AuthManager()
        
        resultado = manager.login(
            email=usuario_cliente_test['email'],
            password="password_incorrecto"
        )
        assert resultado['success'] is False
        assert "Credenciales inválidas" in resultado['message']
    
    @pytest.mark.database
    def test_login_email_inexistente(self):
        """Test: Login con email que no existe"""
        manager = AuthManager()
        
        resultado = manager.login(
            email="no_existe@test.com",
            password="cualquier_password"
        )
        assert resultado['success'] is False
        assert "Usuario no encontrado" in resultado['message']
    
    def test_validar_email_formato(self):
        """Test: Validación de formato de email (método privado)"""
        manager = AuthManager()
        
        # Probar a través de registrarCliente ya que _validar_email es privado
        resultado_valido = manager.registrarCliente(
            nombre="Test Email",
            telefono="111111111",
            email=f"valido_{datetime.now().timestamp()}@example.com",
            direccion="Test",
            password="password123"
        )
        assert resultado_valido['success'] is True, f"Email válido falló: {resultado_valido['message']}"
        
        resultado_invalido = manager.registrarCliente(
            nombre="Test Email",
            telefono="111111111",
            email="email_invalido@",
            direccion="Test",
            password="password123"
        )
        assert resultado_invalido['success'] is False
        assert "inválido" in resultado_invalido['message']
    
    def test_validar_password_seguro(self):
        """Test: Validación de contraseña segura (método privado)"""
        manager = AuthManager()
        
        # Probar a través de registrarCliente ya que _validar_password es privado
        resultado_valido = manager.registrarCliente(
            nombre="Test Pass",
            telefono="111111111",
            email=f"testpass_{datetime.now().timestamp()}@test.com",
            direccion="Test",
            password="pass123"
        )
        assert resultado_valido['success'] is True
        
        resultado_corto = manager.registrarCliente(
            nombre="Test Pass",
            telefono="111111111",
            email=f"testpass2_{datetime.now().timestamp()}@test.com",
            direccion="Test",
            password="12345"
        )
        assert resultado_corto['success'] is False
        assert "6 caracteres" in resultado_corto['message']
class TestUsuarioDAO:
    """Tests para el DAO de Usuario"""
    
    @pytest.mark.database
    def test_crear_usuario(self):
        """Test: Crear usuario en BD"""
        dao = UsuarioDAO()
        usuario = Usuario(
            nombre="Test User",
            email=f"test_user_{datetime.now().timestamp()}@test.com",
            password="testpass123",
            rol="cliente",
            activo=True
        )
        
        resp = dao.crear(usuario)
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['email'] == usuario.email
        assert resp.data[0]['rol'] == 'cliente'
    
    @pytest.mark.database
    def test_obtener_por_email(self, usuario_cliente_test):
        """Test: Obtener usuario por email"""
        if not usuario_cliente_test:
            pytest.skip("No se pudo crear usuario de prueba")
        
        dao = UsuarioDAO()
        resp = dao.obtener_por_email(usuario_cliente_test['email'])
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['id_usuario'] == usuario_cliente_test['id_usuario']
    
    @pytest.mark.database
    def test_modificar_usuario(self, usuario_cliente_test):
        """Test: Modificar datos de usuario"""
        if not usuario_cliente_test:
            pytest.skip("No se pudo crear usuario de prueba")
        
        dao = UsuarioDAO()
        cambios = {"nombre": "Nombre Modificado"}
        
        resp = dao.modificar(usuario_cliente_test['id_usuario'], cambios)
        
        assert resp.data is not None
        assert resp.data[0]['nombre'] == "Nombre Modificado"


class TestClienteDAO:
    """Tests para el DAO de Cliente"""
    
    @pytest.mark.database
    def test_crear_cliente(self, usuario_cliente_test):
        """Test: Crear cliente asociado a usuario"""
        if not usuario_cliente_test:
            pytest.skip("No se pudo crear usuario de prueba")
        
        dao = ClienteDAO()
        cliente = Cliente(
            id_usuario=usuario_cliente_test['id_usuario'],
            telefono="999888777",
            direccion="Av. Test 123"
        )
        
        resp = dao.crear(cliente)
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['id_usuario'] == usuario_cliente_test['id_usuario']
    
    @pytest.mark.database
    def test_obtener_cliente_por_usuario(self, cliente_test):
        """Test: Obtener cliente por ID de usuario"""
        if not cliente_test:
            pytest.skip("No se pudo crear cliente de prueba")
        
        dao = ClienteDAO()
        resp = dao.obtener_por_usuario(cliente_test['id_usuario'])
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['id_cliente'] == cliente_test['id_cliente']


class TestUsuarioEntidad:
    """Tests para la entidad Usuario"""
    
    def test_to_dict_sin_password(self):
        """Test: to_dict() no incluye password por defecto"""
        usuario = Usuario(
            id_usuario=1,
            nombre="Test",
            email="test@test.com",
            password="secret123",
            rol="cliente",
            activo=True
        )
        
        data = usuario.to_dict()
        
        assert 'password' not in data
        assert data['nombre'] == "Test"
        assert data['email'] == "test@test.com"
        assert data['rol'] == "cliente"
    
    def test_to_dict_con_password(self):
        """Test: to_dict() incluye password si se solicita"""
        usuario = Usuario(
            id_usuario=1,
            nombre="Test",
            email="test@test.com",
            password="secret123",
            rol="cliente"
        )
        
        data = usuario.to_dict(incluir_password=True)
        
        assert 'password' in data
        assert data['password'] == "secret123"
    
    def test_from_dict(self):
        """Test: Crear usuario desde diccionario"""
        data = {
            'id_usuario': 1,
            'nombre': 'Test User',
            'email': 'test@example.com',
            'password': 'pass123',
            'rol': 'empleado',
            'activo': True,
            'created_at': '2025-11-27T10:00:00'
        }
        
        usuario = Usuario.from_dict(data)
        
        assert usuario.id_usuario == 1
        assert usuario.nombre == 'Test User'
        assert usuario.email == 'test@example.com'
        assert usuario.rol == 'empleado'
        assert usuario.activo is True
    
    def test_roles_validos(self):
        """Test: Solo acepta roles válidos"""
        usuario = Usuario(rol='cliente')
        assert usuario.rol == 'cliente'
        
        usuario = Usuario(rol='empleado')
        assert usuario.rol == 'empleado'
        
        usuario = Usuario(rol='administrador')
        assert usuario.rol == 'administrador'
        
        # Rol inválido debe convertirse a 'cliente'
        usuario = Usuario(rol='rol_invalido')
        assert usuario.rol == 'cliente'
