from django import forms
from django.db.models import fields
from .models import *


class PlantInfo(forms.ModelForm):
    class Meta:
        model = PlantDetect
        fields= ['userimage']
        labels = {
            'userimage':''
        }
        