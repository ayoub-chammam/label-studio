from .models import labelling_function, weak_annotation_logs
from rest_framework import serializers

class labelling_function_serializer(serializers.ModelSerializer):

    class Meta:
        model = labelling_function
        fields = ('__all__')

class weak_annotation_serializer(serializers.ModelSerializer):

    class Meta:
        model = weak_annotation_logs
        fields = ['project']