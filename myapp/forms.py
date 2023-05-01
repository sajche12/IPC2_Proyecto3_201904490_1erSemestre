from django import forms

class CargarDatos(forms.Form):
    usuario = forms.CharField(label="Usuario")
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)
