# bodega/urls.py (crear este archivo en tu app)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inventario/', views.inventario, name='inventario'),
    path('inventario/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('inventario/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('retiros/', views.retiros, name='retiros'),
    path('devolver/<int:retiro_id>/', views.devolver_producto, name='devolver_producto'),
    path('consulta/', views.consulta_usuario, name='consulta_usuario'),
    path('usuarios/', views.usuarios, name='usuarios'),
]
