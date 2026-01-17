from django.contrib import admin
from django.urls import path # Quitamos 'include' porque no lo usaremos aquí
from django.contrib.auth import views as auth_views
from mantenimiento import views

urlpatterns = [
    # 1. Panel de Admin
    path('admin/', admin.site.urls),

    # 2. Login y Logout
    path('accounts/login/', auth_views.LoginView.as_view(template_name='mantenimiento/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. Rutas de la App
    path('tablero/', views.tablero, name='tablero'),
    path('trabajo/', views.lista_trabajo, name='trabajo'),
    path('comenzar/<int:orden_id>/', views.comenzar_orden, name='comenzar_orden'),
    path('finalizar/<int:orden_id>/', views.finalizar_orden, name='finalizar_orden'),
    path('generar/', views.generar_ordenes, name='generar_ordenes'),
    path('crear-plan/', views.crear_plan, name='crear_plan'),
    path('exportar/', views.exportar_ordenes_csv, name='exportar_csv'),
    path('activos/', views.lista_activos, name='lista_activos'),
    path('activos/editar/<int:activo_id>/', views.editar_activo, name='editar_activo'),
    path('activos/nuevo/', views.crear_activo, name='crear_activo'),
    path('activos/eliminar/<int:activo_id>/', views.eliminar_activo, name='eliminar_activo'),
    
    # Ruta raíz: Si alguien entra a la página principal, lo mandamos al tablero
    path('', views.tablero, name='raiz'),
]