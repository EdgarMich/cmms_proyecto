import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo.settings')
django.setup()

from mantenimiento.models import Activo, Area

def importar_activos():
    area_cnc, _ = Area.objects.get_or_create(nombre='CNC')
    archivo_ruta = 'activos.csv'
    
    if not os.path.exists(archivo_ruta):
        print(f"Error: No encuentro el archivo {archivo_ruta}")
        return

    with open(archivo_ruta, 'r', encoding='utf-8-sig') as f:
        # Forzamos que el delimitador sea una coma basándonos en lo que viste
        reader = csv.DictReader(f, delimiter=',')
        
        conteo = 0
        for row in reader:
            # Según tu Bloc de Notas, las columnas se llaman así:
            tag = row.get('3 Codigo Activo') or row.get('Codigo Activo')
            desc = row.get('1 Nombre') or row.get('Nombre') or row.get('Nombre / Arc.Locacion')

            if tag and desc:
                activo, created = Activo.objects.get_or_create(
                    codigo=tag.strip(),
                    defaults={
                        'descripcion': desc.strip(),
                        'area': area_cnc,
                        'estatus_activo': True
                    }
                )
                if created:
                    conteo += 1
                    print(f"Agregado: {tag}")
            
    print(f"\n--- TERMINADO: Se agregaron {conteo} activos nuevos ---")

if __name__ == '__main__':
    importar_activos()