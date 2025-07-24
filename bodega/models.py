# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Categoria(models.Model):
    CATEGORIAS_CHOICES = [
        ('aseo', 'Artículos de Aseo'),
        ('oficina', 'Artículos de Oficina'),
        ('tecnologia', 'Tecnología'),
        ('limpieza', 'Limpieza'),
        ('herramientas', 'Herramientas'),
        ('mobiliario', 'Mobiliario'),
        ('consumibles', 'Consumibles'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=50, choices=CATEGORIAS_CHOICES, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.get_nombre_display()
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    cantidad = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.nombre} - {self.categoria} (ID: {self.id})"
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['categoria', 'nombre']

class Usuario(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombre} - {self.rut}"
    
    def retiros_recientes(self, producto_id):
        """Verifica si hay retiros del mismo producto en el último mes"""
        hace_un_mes = timezone.now() - timedelta(days=30)
        return self.retiro_set.filter(
            producto_id=producto_id,
            fecha_retiro__gte=hace_un_mes,
            devuelto=False
        ).exists()
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

class Retiro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_retiro = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)
    
    def __str__(self):
        estado = "Devuelto" if self.devuelto else "Pendiente"
        return f"{self.usuario.nombre} - {self.producto.nombre} ({estado})"
    
    def marcar_devuelto(self):
        self.devuelto = True
        self.fecha_devolucion = timezone.now()
        self.save()
        # Devolver stock al producto
        self.producto.cantidad += 1
        self.producto.save()
    
    class Meta:
        verbose_name = "Retiro"
        verbose_name_plural = "Retiros"
        ordering = ['-fecha_retiro']