from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import LoginForm, UsuarioCreateForm, UsuarioEditForm
from .models import Docente, Carrera, Periodo, DocenteTransaccional

Usuario = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            password = form.cleaned_data['password']
            user = authenticate(request, cedula=cedula, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
            else:
                form.add_error(None, 'Cédula o contraseña incorrectos')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


@login_required
def dashboard_view(request):
    usuario = request.user
    context = {}

    if usuario.is_superuser or usuario.groups.filter(name='Administrador').exists():
        context.update({
            'total_docentes': Docente.objects.count(),
            'total_carreras': Carrera.objects.count(),
            'total_periodos': Periodo.objects.count(),
            'total_asignaciones': DocenteTransaccional.objects.count(),
            'ultimos_docentes': Docente.objects.order_by('-id')[:5],
        })

    return render(request, 'core/dashboard.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def mi_perfil_view(request):
    return redirect('core:dashboard')


@login_required
def mis_titulos_view(request):
    return redirect('core:dashboard')


@login_required
def crear_titulo_view(request):
    return redirect('core:dashboard')


@login_required
def mis_publicaciones_view(request):
    return redirect('core:dashboard')


@login_required
def crear_publicacion_view(request):
    return redirect('core:dashboard')


@login_required
def mis_documentos_view(request):
    return redirect('core:dashboard')


@login_required
def mis_cursos_view(request):
    return redirect('core:dashboard')


@login_required
def subir_documento_view(request):
    return redirect('core:dashboard')


def _require_admin(user):
    if not (user.is_superuser or user.groups.filter(name='Administrador').exists()):
        raise PermissionDenied
    return True


@login_required
def usuarios_list_view(request):
    if not _require_admin(request.user):
        return
    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'core/usuarios_list.html', {
        'usuarios': usuarios,
    })


@login_required
def usuario_crear_view(request):
    if not _require_admin(request.user):
        return
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            Docente.objects.get_or_create(
                cedula=user.cedula,
                defaults={'apellidos_nombres': f'Usuario {user.cedula}'}
            )
            messages.success(request, f'Usuario {user.cedula} creado correctamente.')
            return redirect('core:usuarios_list')
    else:
        form = UsuarioCreateForm()
    return render(request, 'core/usuario_form.html', {
        'form': form,
        'accion': 'Crear',
    })


@login_required
def usuario_editar_view(request, usuario_id):
    if not _require_admin(request.user):
        return
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.cedula} actualizado.')
            return redirect('core:usuarios_list')
    else:
        form = UsuarioEditForm(instance=usuario)
    return render(request, 'core/usuario_form.html', {
        'form': form,
        'usuario': usuario,
        'accion': 'Editar',
    })
