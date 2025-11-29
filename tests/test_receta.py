from django.test import TestCase

from dao.productoInsumoDAO import ProductoInsumoDAO

# Fake Supabase minimal para pruebas de receta
class FakeTable:
    def __init__(self, name, store):
        self.name = name
        self.store = store
        self._pending_delete_filter = None
        self._pending_insert = None
        self._mode = None
        self._filters = []

    # Chainable mocks
    def delete(self):
        self._mode = 'delete'
        return self

    def select(self, cols='*'):
        self._mode = 'select'
        return self

    def order(self, col):
        # ordering no es relevante para pruebas
        return self

    def eq(self, col, value):
        if self._mode == 'delete' and col == 'id_producto':
            self._pending_delete_filter = value
        else:
            self._filters.append((col, value))
        return self

    def insert(self, data):
        self._pending_insert = data
        return self

    def execute(self):
        if self._mode == 'delete' and self._pending_delete_filter is not None:
            self.store[:] = [r for r in self.store if r.get('id_producto') != self._pending_delete_filter]
            self._pending_delete_filter = None
            self._mode = None
            return type('Resp', (), {'data': []})()
        if self._mode == 'select':
            data = self.store
            for col, val in self._filters:
                data = [r for r in data if r.get(col) == val]
            # reset
            self._filters = []
            self._mode = None
            return type('Resp', (), {'data': data})()
        if self._pending_insert is not None:
            inserted = []
            if isinstance(self._pending_insert, list):
                for row in self._pending_insert:
                    row = dict(row)
                    row['id_producto_insumo'] = len(self.store) + 1
                    self.store.append(row)
                    inserted.append(row)
            else:
                row = dict(self._pending_insert)
                row['id_producto_insumo'] = len(self.store) + 1
                self.store.append(row)
                inserted.append(row)
            self._pending_insert = None
            return type('Resp', (), {'data': inserted})()
        return type('Resp', (), {'data': []})()

class FakeSupabase:
    def __init__(self):
        self.data_store = []  # lista de producto_insumo

    def table(self, name):
        assert name == 'producto_insumo'
        return FakeTable(name, self.data_store)

class RecetaTests(TestCase):
    def setUp(self):
        # Monkeypatch get_supabase_client para usar fake
        from config import get_supabase_client
        import config
        config._supabase_client = FakeSupabase()  # Forzar singleton
        self.dao = ProductoInsumoDAO()

    def test_reemplazar_receta_merge_duplicados(self):
        lista = [
            {'id_insumo': 1, 'cantidad_necesaria': 2},
            {'id_insumo': 1, 'cantidad_necesaria': 3},
            {'id_insumo': 2, 'cantidad_necesaria': 4},
            {'id_insumo': 2, 'cantidad_necesaria': -1},  # se ignora negativa
        ]
        res = self.dao.reemplazar_insumos_de_producto(10, lista)
        self.assertEqual(len(res), 2)
        cantidades = {r.id_insumo: r.cantidad_necesaria for r in res}
        self.assertEqual(cantidades[1], 5.0)
        self.assertEqual(cantidades[2], 4.0)

    def test_reemplazar_receta_todo_invalido(self):
        lista = [
            {'id_insumo': 1, 'cantidad_necesaria': 0},
            {'id_insumo': 2, 'cantidad_necesaria': -5},
        ]
        res = self.dao.reemplazar_insumos_de_producto(11, lista)
        self.assertEqual(res, [])

    def test_calcular_costo_producto(self):
        lista = [
            {'id_insumo': 1, 'cantidad_necesaria': 2},
            {'id_insumo': 2, 'cantidad_necesaria': 4},
        ]
        self.dao.reemplazar_insumos_de_producto(12, lista)
        costo = self.dao.calcular_costo_producto(12, {1: 10.0, 2: 1.5})
        # 2*10 + 4*1.5 = 20 + 6 = 26
        self.assertEqual(costo, 26.0)
