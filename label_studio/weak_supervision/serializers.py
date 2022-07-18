from .models import aggregate_result, labelling_function, weak_annotation_log, result
from rest_framework import serializers

class labelling_function_serializer(serializers.ModelSerializer):

    class Meta:
        model = labelling_function
        fields = ('__all__')

class labelling_function_results_serializer(serializers.ModelSerializer):

    class Meta:
        model = result
        fields = ['id', 'function']


class weak_annotation_serializer(serializers.ModelSerializer):

    class Meta:
        model = weak_annotation_log
        fields = ['project']



class aggregate_results_serializer(serializers.ModelSerializer):

    class Meta:
        model = aggregate_result
        fields = ['model_name', 'model_type', 'project']