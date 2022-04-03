from rest_framework import serializers
from .models import PlantDetect

class DiseaseDetectSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlantDetect
        fields = '__all__'


class Imageserializer(serializers.ModelSerializer):

    class Meta:
        
        model = PlantDetect
        fields = ['userimage']
        # field = base64.encodebytes(field).decode('utf-8')
        # field = json.dumps(field)