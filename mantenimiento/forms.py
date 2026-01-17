from django import forms
from .models import PlanPM, Activo

class PlanPMForm(forms.ModelForm):
    class Meta:
        model = PlanPM
        # Agrega 'fecha_proxima_ejecucion' a la lista:
        fields = ['activo', 'plantilla', 'frecuencia_meses', 'fecha_proxima_ejecucion']
        # Esto hace que aparezca un calendario en lugar de un cuadro de texto:
        widgets = {
            'fecha_proxima_ejecucion': forms.DateInput(attrs={'type': 'date'}),
        }
		
class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        fields = ['codigo', 'descripcion', 'area', 'estatus_activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'estatus_activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }