from django.contrib import admin
from .models import Producto, Usuario, Retiro, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_display', 'descripcion', 'total_productos']
    list_filter = ['nombre']
    search_fields = ['nombre', 'descripcion']
    
    def total_productos(self, obj):
        return obj.productos.count()
    total_productos.short_description = 'Total Productos'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'categoria', 'cantidad', 'estado_stock']
    list_filter = ['categoria', 'cantidad']
    search_fields = ['nombre', 'categoria__nombre']
    ordering = ['categoria', 'nombre']
    
    def estado_stock(self, obj):
        if obj.cantidad > 5:
            return "Stock Normal"
        elif obj.cantidad > 0:
            return "Stock Bajo"
        else:
            return "Sin Stock"
    estado_stock.short_description = 'Estado'

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['rut', 'nombre', 'total_retiros', 'retiros_pendientes']
    search_fields = ['rut', 'nombre']
    
    def total_retiros(self, obj):
        return obj.retiro_set.count()
    total_retiros.short_description = 'Total Retiros'
    
    def retiros_pendientes(self, obj):
        return obj.retiro_set.filter(devuelto=False).count()
    retiros_pendientes.short_description = 'Pendientes'

@admin.register(Retiro)
class RetiroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'categoria_producto', 'fecha_retiro', 'devuelto']
    list_filter = ['devuelto', 'fecha_retiro', 'producto__categoria']
    search_fields = ['usuario__nombre', 'producto__nombre']
    ordering = ['-fecha_retiro']
    
    def categoria_producto(self, obj):
        return obj.producto.categoria
    categoria_producto.short_description = 'Categoría'