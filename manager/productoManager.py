#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.productoDAO import ProductoDAO
from entidades.producto import Producto


class ProductoManager:
    """
    Manager para la gestión de productos con lógica de negocio
    """
    
    def __init__(self):
        """Constructor que inicializa el DAO"""
        self.producto_dao = ProductoDAO()
    
    def crearProducto(self, codigo, nombre, descripcion, id_unidad, contenido, precio, stock=0):
        """
        Crea un nuevo producto con validaciones
        
        Args:
            codigo: Código único del producto
            nombre: Nombre del producto
            descripcion: Descripción detallada
            id_unidad: ID de la unidad de medida
            contenido: Contenido/cantidad por unidad
            precio: Precio del producto
            stock: Stock inicial (default 0)
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'producto': Producto}
        """
        # Validaciones
        if not codigo or not codigo.strip():
            return {
                'exito': False,
                'mensaje': 'El código del producto es requerido',
                'producto': None
            }
        
        if not nombre or not nombre.strip():
            return {
                'exito': False,
                'mensaje': 'El nombre del producto es requerido',
                'producto': None
            }
        
        # Validar que el código no esté duplicado
        producto_existente = self.producto_dao.obtener_por_codigo(codigo)
        if producto_existente:
            return {
                'exito': False,
                'mensaje': f'Ya existe un producto con el código {codigo}',
                'producto': None
            }
        
        # Validar precio
        try:
            precio_decimal = float(precio)
            if precio_decimal < 0:
                return {
                    'exito': False,
                    'mensaje': 'El precio no puede ser negativo',
                    'producto': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'El precio debe ser un número válido',
                'producto': None
            }
        
        # Validar stock
        try:
            stock_int = int(stock)
            if stock_int < 0:
                return {
                    'exito': False,
                    'mensaje': 'El stock no puede ser negativo',
                    'producto': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'El stock debe ser un número entero válido',
                'producto': None
            }
        
        # Validar contenido
        try:
            contenido_decimal = float(contenido)
            if contenido_decimal <= 0:
                return {
                    'exito': False,
                    'mensaje': 'El contenido debe ser mayor a 0',
                    'producto': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'El contenido debe ser un número válido',
                'producto': None
            }
        
        # Crear objeto Producto
        nuevo_producto = Producto(
            id_producto=None,
            codigo=codigo.strip(),
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else '',
            id_unidad=id_unidad,
            contenido=contenido_decimal,
            precio=precio_decimal,
            stock=stock_int,
            activo=True
        )
        
        # Insertar en la base de datos
        producto_creado = self.producto_dao.insertar(nuevo_producto)
        
        if producto_creado:
            return {
                'exito': True,
                'mensaje': 'Producto creado exitosamente',
                'producto': producto_creado
            }
        else:
            return {
                'exito': False,
                'mensaje': 'Error al crear el producto en la base de datos',
                'producto': None
            }
    
    def modificarProducto(self, id_producto, datos):
        """
        Modifica un producto existente con validaciones
        
        Args:
            id_producto: ID del producto a modificar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'producto': Producto}
        """
        # Verificar que el producto existe
        producto_existente = self.producto_dao.obtener_por_id(id_producto)
        if not producto_existente:
            return {
                'exito': False,
                'mensaje': 'Producto no encontrado',
                'producto': None
            }
        
        # Si se está modificando el código, validar que no esté duplicado
        if 'codigo' in datos:
            otro_producto = self.producto_dao.obtener_por_codigo(datos['codigo'])
            if otro_producto and otro_producto.id_producto != id_producto:
                return {
                    'exito': False,
                    'mensaje': f'Ya existe otro producto con el código {datos["codigo"]}',
                    'producto': None
                }
        
        # Validar nombre si se está actualizando
        if 'nombre' in datos:
            if not datos['nombre'] or not datos['nombre'].strip():
                return {
                    'exito': False,
                    'mensaje': 'El nombre del producto no puede estar vacío',
                    'producto': None
                }
            datos['nombre'] = datos['nombre'].strip()
        
        # Validar precio si se está actualizando
        if 'precio' in datos:
            try:
                precio_decimal = float(datos['precio'])
                if precio_decimal < 0:
                    return {
                        'exito': False,
                        'mensaje': 'El precio no puede ser negativo',
                        'producto': None
                    }
                datos['precio'] = precio_decimal
            except (ValueError, TypeError):
                return {
                    'exito': False,
                    'mensaje': 'El precio debe ser un número válido',
                    'producto': None
                }
        
        # Validar stock si se está actualizando
        if 'stock' in datos:
            try:
                stock_int = int(datos['stock'])
                if stock_int < 0:
                    return {
                        'exito': False,
                        'mensaje': 'El stock no puede ser negativo',
                        'producto': None
                    }
                datos['stock'] = stock_int
            except (ValueError, TypeError):
                return {
                    'exito': False,
                    'mensaje': 'El stock debe ser un número entero válido',
                    'producto': None
                }
        
        # Validar contenido si se está actualizando
        if 'contenido' in datos:
            try:
                contenido_decimal = float(datos['contenido'])
                if contenido_decimal <= 0:
                    return {
                        'exito': False,
                        'mensaje': 'El contenido debe ser mayor a 0',
                        'producto': None
                    }
                datos['contenido'] = contenido_decimal
            except (ValueError, TypeError):
                return {
                    'exito': False,
                    'mensaje': 'El contenido debe ser un número válido',
                    'producto': None
                }
        
        # Actualizar producto
        producto_actualizado = self.producto_dao.actualizar(id_producto, datos)
        
        if producto_actualizado:
            return {
                'exito': True,
                'mensaje': 'Producto actualizado exitosamente',
                'producto': producto_actualizado
            }
        else:
            return {
                'exito': False,
                'mensaje': 'Error al actualizar el producto',
                'producto': None
            }
    
    def listarProductos(self, solo_activos=False, stock_bajo=False, stock_minimo=10):
        """
        Lista productos con diferentes filtros
        
        Args:
            solo_activos: Si True, solo devuelve productos activos
            stock_bajo: Si True, solo devuelve productos con stock bajo
            stock_minimo: Umbral para considerar stock bajo
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'productos': list}
        """
        try:
            if stock_bajo:
                productos = self.producto_dao.listar_con_stock_bajo(stock_minimo)
                mensaje = f'Productos con stock menor a {stock_minimo}'
            elif solo_activos:
                productos = self.producto_dao.listar_activos()
                mensaje = 'Productos activos'
            else:
                productos = self.producto_dao.listar_todos()
                mensaje = 'Todos los productos'
            
            return {
                'exito': True,
                'mensaje': mensaje,
                'productos': productos
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al listar productos: {str(e)}',
                'productos': []
            }
    
    def obtenerProducto(self, id_producto):
        """
        Obtiene un producto por ID
        
        Args:
            id_producto: ID del producto
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'producto': Producto}
        """
        producto = self.producto_dao.obtener_por_id(id_producto)
        
        if producto:
            return {
                'exito': True,
                'mensaje': 'Producto encontrado',
                'producto': producto
            }
        else:
            return {
                'exito': False,
                'mensaje': 'Producto no encontrado',
                'producto': None
            }
    
    def buscarProductos(self, termino):
        """
        Busca productos por nombre
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'productos': list}
        """
        if not termino or not termino.strip():
            return {
                'exito': False,
                'mensaje': 'Debe proporcionar un término de búsqueda',
                'productos': []
            }
        
        productos = self.producto_dao.buscar_por_nombre(termino.strip())
        
        return {
            'exito': True,
            'mensaje': f'Búsqueda completada: {len(productos)} resultados',
            'productos': productos
        }
    
    def cambiarEstado(self, id_producto, activo):
        """
        Cambia el estado de un producto (activo/inactivo)
        
        Args:
            id_producto: ID del producto
            activo: True para activar, False para desactivar
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'producto': Producto}
        """
        # Verificar que el producto existe
        producto_existente = self.producto_dao.obtener_por_id(id_producto)
        if not producto_existente:
            return {
                'exito': False,
                'mensaje': 'Producto no encontrado',
                'producto': None
            }
        
        producto_actualizado = self.producto_dao.cambiar_estado(id_producto, activo)
        
        if producto_actualizado:
            estado_texto = 'activado' if activo else 'desactivado'
            return {
                'exito': True,
                'mensaje': f'Producto {estado_texto} exitosamente',
                'producto': producto_actualizado
            }
        else:
            return {
                'exito': False,
                'mensaje': 'Error al cambiar el estado del producto',
                'producto': None
            }
    
    def actualizarStock(self, id_producto, cantidad, operacion='sumar'):
        """
        Actualiza el stock de un producto
        
        Args:
            id_producto: ID del producto
            cantidad: Cantidad a sumar o restar
            operacion: 'sumar' o 'restar'
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'producto': Producto}
        """
        # Verificar que el producto existe
        producto_existente = self.producto_dao.obtener_por_id(id_producto)
        if not producto_existente:
            return {
                'exito': False,
                'mensaje': 'Producto no encontrado',
                'producto': None
            }
        
        # Validar cantidad
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                return {
                    'exito': False,
                    'mensaje': 'La cantidad no puede ser negativa',
                    'producto': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'La cantidad debe ser un número entero válido',
                'producto': None
            }
        
        # Validar operación
        if operacion not in ['sumar', 'restar']:
            return {
                'exito': False,
                'mensaje': 'La operación debe ser "sumar" o "restar"',
                'producto': None
            }
        
        producto_actualizado = self.producto_dao.actualizar_stock(id_producto, cantidad_int, operacion)
        
        if producto_actualizado:
            accion = 'sumadas' if operacion == 'sumar' else 'restadas'
            return {
                'exito': True,
                'mensaje': f'Stock actualizado: {cantidad_int} unidades {accion}',
                'producto': producto_actualizado
            }
        else:
            return {
                'exito': False,
                'mensaje': 'Error al actualizar el stock',
                'producto': None
            }

    def verificar_disponibilidad(self, id_producto, cantidad):
        """
        Verifica si un producto tiene stock disponible para la cantidad solicitada.

        Args:
            id_producto: ID del producto
            cantidad: Cantidad solicitada

        Returns:
            bool: True si hay stock suficiente, False en caso contrario o si no existe el producto
        """
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return False
        except (TypeError, ValueError):
            return False

        producto = self.producto_dao.obtener_por_id(id_producto)
        if not producto:
            return False
        try:
            return int(producto.stock) >= cantidad_int
        except Exception:
            return False
