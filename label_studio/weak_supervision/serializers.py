from .models import labelling_function
from rest_framework import serializers

class labelling_function_serializer(serializers.ModelSerializer):

    class Meta:
        model = labelling_function
        fields = ('__all__')