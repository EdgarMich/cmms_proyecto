import datetime
from .models import PlanPM, OrdenTrabajo

def generar_ordenes_mes_actual():
    hoy = datetime.date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    planes = PlanPM.objects.all()
    ordenes_creadas = 0

    for plan in planes:
        # Lógica de ventanas de tiempo
        if plan.semana_objetivo == 'TEMPRANA':
            inicio = datetime.date(anio_actual, mes_actual, 1)
            fin = datetime.date(anio_actual, mes_actual, 10)
        elif plan.semana_objetivo == 'MEDIA':
            inicio = datetime.date(anio_actual, mes_actual, 11)
            fin = datetime.date(anio_actual, mes_actual, 20)
        else: # TARDIA
            inicio = datetime.date(anio_actual, mes_actual, 21)
            # Cálculo simple para el último día del mes
            proximo_mes = hoy.replace(day=28) + datetime.timedelta(days=4)
            fin = proximo_mes - datetime.timedelta(days=proximo_mes.day)

        # Evitar duplicados para el mismo mes/plan
        existe = OrdenTrabajo.objects.filter(
            plan=plan, 
            fecha_inicio_ventana=inicio
        ).exists()

        if not existe:
            OrdenTrabajo.objects.create(
                plan=plan,
                fecha_inicio_ventana=inicio,
                fecha_fin_ventana=fin,
                estado='PENDIENTE'
            )
            ordenes_creadas += 1
            
    return ordenes_creadas