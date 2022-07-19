from .models import aggregate_result, aggregation_model, labelling_function, metric, weak_annotation_log, result
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

class aggregation_model_serializer(serializers.ModelSerializer):

    class Meta:
        model = aggregation_model
        fields = ('__all__')

class aggregate_results_serializer(serializers.ModelSerializer):

    class Meta:
        model = aggregate_result
        fields = ['model_name', 'model_type', 'project']

class metrics_applier_serializer(serializers.ModelSerializer):

    class Meta:
        model = metric
        fields = ['project']