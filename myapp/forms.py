from django import forms

class CargarXml(forms.Form):
    usuario = forms.CharField(label="Usuario")
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)