import csv
import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# --- IMPORTA ESTO PARA LA SEGURIDAD DE SUPERVISOR ---
from django.contrib.admin.views.decorators import staff_member_required
# ----------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from calendar import monthrange
from .models import OrdenTrabajo, Activo, PlanPM
from .forms import PlanPMForm, ActivoForm

# VISTAS ACCESIBLES PARA TODOS (TÉCNICOS Y SUPERVISORES)
@login_required
def tablero(request):
    hoy = timezone.now().date()
    total_activos = Activo.objects.filter(estatus_activo=True).count()
    pendientes = OrdenTrabajo.objects.filter(estado='PENDIENTE', fecha_inicio_ventana__month=hoy.month).count()
    completadas = OrdenTrabajo.objects.filter(estado='COMPLETADO', fecha_inicio_ventana__month=hoy.month).count()
    en_proceso = OrdenTrabajo.objects.filter(estado='PROCESO', fecha_inicio_ventana__month=hoy.month).count()
    
    lunes = hoy - timedelta(days=hoy.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]
    
    completadas_semana = OrdenTrabajo.objects.filter(
        estado='COMPLETADO',
        fecha_finalizado__date__range=[lunes, lunes + timedelta(days=6)]
    )
    
    datos_semanal = []
    for dia in dias_semana:
        conteo = completadas_semana.filter(fecha_finalizado__date=dia).count()
        datos_semanal.append(conteo)
    
    labels_semanal = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    return render(request, 'mantenimiento/tablero.html', {
        'total_activos': total_activos,
        'pendientes': pendientes, 
        'completadas': completadas, 
        'en_proceso': en_proceso, 
        'hoy': hoy,
        'labels_semanal': labels_semanal,
        'datos_semanal': datos_semanal,
    })

@login_required
def lista_trabajo(request):
    hoy = timezone.now().date()
    ordenes = OrdenTrabajo.objects.filter(estado__in=['PENDIENTE', 'PROCESO'], fecha_inicio_ventana__month=hoy.month)
    return render(request, 'mantenimiento/trabajo.html', {'ordenes': ordenes})

@login_required
def comenzar_orden(request, orden_id):
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, id=orden_id)
        orden.estado = 'PROCESO'
        orden.save()
    return redirect('trabajo')

@login_required
def finalizar_orden(request, orden_id):
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, id=orden_id)
        orden.estado = 'COMPLETADO'
        orden.fecha_finalizado = timezone.now()
        orden.save()
    return redirect('trabajo')

@login_required
def lista_activos(request):
    activos = Activo.objects.all().order_by('area', 'codigo')
    return render(request, 'mantenimiento/activos.html', {'activos': activos})


# VISTAS RESTRINGIDAS (SOLO SUPERVISORES / STAFF)
@staff_member_required # <--- SEGURIDAD REAL
def generar_ordenes(request):
    hoy = timezone.now().date()
    planes = PlanPM.objects.all()
    for plan in planes:
        if plan.fecha_proxima_ejecucion <= hoy:
            inicio = plan.fecha_proxima_ejecucion.replace(day=1)
            ultimo_dia = monthrange(plan.fecha_proxima_ejecucion.year, plan.fecha_proxima_ejecucion.month)[1]
            fin = plan.fecha_proxima_ejecucion.replace(day=ultimo_dia)
            
            existe = OrdenTrabajo.objects.filter(
                plan=plan, 
                fecha_inicio_ventana__month=plan.fecha_proxima_ejecucion.month,
                fecha_inicio_ventana__year=plan.fecha_proxima_ejecucion.year
            ).exists()
            
            if not existe:
                OrdenTrabajo.objects.create(
                    plan=plan,
                    fecha_inicio_ventana=inicio,
                    fecha_fin_ventana=fin,
                    estado='PENDIENTE'
                )
                nueva_fecha = plan.fecha_proxima_ejecucion + datetime.timedelta(days=31)
                plan.fecha_proxima_ejecucion = nueva_fecha.replace(day=1)
                plan.save()
    return redirect('tablero')

@staff_member_required
def crear_plan(request):
    form = PlanPMForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('tablero')
    return render(request, 'mantenimiento/crear_plan.html', {'form': form})

@staff_member_required
def crear_activo(request):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_activos')
    else:
        form = ActivoForm()
    return render(request, 'mantenimiento/crear_activo.html', {'form': form})

@staff_member_required
def editar_activo(request, activo_id):
    activo = get_object_or_404(Activo, id=activo_id)
    if request.method == 'POST':
        form = ActivoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            return redirect('lista_activos')
    else:
        form = ActivoForm(instance=activo)
    return render(request, 'mantenimiento/editar_activo.html', {'form': form, 'activo': activo})

@staff_member_required
def eliminar_activo(request, activo_id):
    activo = get_object_or_404(Activo, id=activo_id)
    if request.method == 'POST':
        activo.delete()
        return redirect('lista_activos')
    return redirect('lista_activos')

@staff_member_required
def exportar_ordenes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ordenes_mantenimiento.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Activo', 'Plantilla', 'Fecha Inicio', 'Fecha Fin', 'Estado'])
    ordenes = OrdenTrabajo.objects.all()
    for ot in ordenes:
        writer.writerow([ot.id, ot.plan.activo.codigo, ot.plan.plantilla.nombre, ot.fecha_inicio_ventana, ot.fecha_fin_ventana, ot.estado])
    return response