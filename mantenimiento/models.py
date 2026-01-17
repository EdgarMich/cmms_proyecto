from django.db import models

# 1. Áreas de la planta
class Area(models.Model):
    nombre = models.CharField(max_length=50) 
    def __str__(self): return self.nombre

# 2. Activos (Máquinas)
class Activo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    estatus_activo = models.BooleanField(default=True)

    def __str__(self): return f"{self.codigo} - {self.descripcion}"

# 3. Qué se va a hacer (La hoja de papel)
class PlantillaPM(models.Model):
    nombre = models.CharField(max_length=100)
    checklist = models.TextField(help_text="Escribe aquí las tareas")
    def __str__(self): return self.nombre

# mantenimiento/models.py

class PlanPM(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='planes')
    plantilla = models.ForeignKey(PlantillaPM, on_delete=models.PROTECT)
    frecuencia_meses = models.IntegerField(default=1, help_text="Cada cuántos meses")
    # AGREGA ESTA LÍNEA AQUÍ ABAJO:
    fecha_proxima_ejecucion = models.DateField(null=True, blank=True, verbose_name="Mes de inicio")

    def __str__(self):
        return f"Plan {self.plantilla.nombre} - {self.activo.codigo}"

# 5. La Orden de Trabajo (Lo que el técnico ve)
class OrdenTrabajo(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
    ]

    plan = models.ForeignKey(PlanPM, on_delete=models.CASCADE)
    fecha_inicio_ventana = models.DateField()
    fecha_fin_ventana = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    comentarios = models.TextField(blank=True)
    
    fecha_finalizado = models.DateTimeField(null=True, blank=True) 
   
    def __str__(self):
        return f"OT #{self.id} - {self.plan.activo.codigo}"