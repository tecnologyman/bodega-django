# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Producto, Usuario, Retiro, Categoria
from .forms import ProductoForm, UsuarioForm, RetiroForm, CategoriaForm

def home(request):
    return render(request, 'bodega/home.html')

# Vista del inventario
def inventario(request):
    categoria_filtro = request.GET.get('categoria')
    
    if categoria_filtro:
        productos = Producto.objects.filter(categoria__nombre=categoria_filtro)
    else:
        productos = Producto.objects.all()
    
    categorias = Categoria.objects.all()
    form = ProductoForm()
    categoria_form = CategoriaForm()
    
    if request.method == 'POST':
        if 'agregar_producto' in request.POST:
            form = ProductoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Producto agregado exitosamente')
                return redirect('inventario')
        elif 'agregar_categoria' in request.POST:
            categoria_form = CategoriaForm(request.POST)
            if categoria_form.is_valid():
                categoria_form.save()
                messages.success(request, 'Categoría agregada exitosamente')
                return redirect('inventario')
    
    # Agrupar productos por categoría
    productos_por_categoria = {}
    for categoria in categorias:
        productos_categoria = productos.filter(categoria=categoria)
        if productos_categoria.exists():
            productos_por_categoria[categoria] = productos_categoria
    
    return render(request, 'bodega/inventario.html', {
        'productos': productos,
        'categorias': categorias,
        'productos_por_categoria': productos_por_categoria,
        'categoria_filtro': categoria_filtro,
        'form': form,
        'categoria_form': categoria_form
    })

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('inventario')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'bodega/editar_producto.html', {
        'form': form,
        'producto': producto
    })

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
    return redirect('inventario')

# Vista de retiros
def retiros(request):
    form = RetiroForm()
    
    if request.method == 'POST':
        form = RetiroForm(request.POST)
        if form.is_valid():
            retiro = form.save(commit=False)
            
            # Verificar si hay stock disponible
            if retiro.producto.cantidad <= 0:
                messages.error(request, 'No hay stock disponible para este producto')
                return render(request, 'bodega/retiros.html', {'form': form})
            
            # Verificar retiros recientes
            if retiro.usuario.retiros_recientes(retiro.producto.id):
                messages.warning(request, 
                    f'¡ATENCIÓN! El usuario {retiro.usuario.nombre} ya retiró este producto recientemente (último mes)')
            
            # Guardar retiro y reducir stock
            retiro.save()
            retiro.producto.cantidad -= 1
            retiro.producto.save()
            
            messages.success(request, 'Retiro registrado exitosamente')
            return redirect('retiros')
    
    retiros_pendientes = Retiro.objects.filter(devuelto=False)
    return render(request, 'bodega/retiros.html', {
        'form': form,
        'retiros_pendientes': retiros_pendientes
    })

def devolver_producto(request, retiro_id):
    retiro = get_object_or_404(Retiro, id=retiro_id, devuelto=False)
    
    if request.method == 'POST':
        retiro.marcar_devuelto()
        messages.success(request, f'Producto {retiro.producto.nombre} devuelto exitosamente')
    
    return redirect('retiros')

# Vista de consulta por usuario
def consulta_usuario(request):
    usuario = None
    retiros = []
    retiros_pendientes = 0
    
    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuario.objects.get(rut=rut)
            retiros = Retiro.objects.filter(usuario=usuario)
            retiros_pendientes = retiros.filter(devuelto=False).count()
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    
    return render(request, 'bodega/consulta_usuario.html', {
        'usuario': usuario,
        'retiros': retiros,
        'retiros_pendientes': retiros_pendientes
    })

# Vista para gestionar usuarios
def usuarios(request):
    usuarios_list = Usuario.objects.all()
    form = UsuarioForm()
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario agregado exitosamente')
            return redirect('usuarios')
    
    # Agregar contadores para cada usuario
    usuarios_con_stats = []
    total_retiros_activos = 0
    
    for usuario in usuarios_list:
        retiros_activos = usuario.retiro_set.filter(devuelto=False).count()
        total_retiros = usuario.retiro_set.count()
        
        usuario.retiros_activos = retiros_activos
        usuario.total_retiros = total_retiros
        total_retiros_activos += retiros_activos
        
        usuarios_con_stats.append(usuario)
    
    return render(request, 'bodega/usuarios.html', {
        'usuarios': usuarios_con_stats,
        'form': form,
        'total_retiros_activos': total_retiros_activos
    })