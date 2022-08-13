from .models import aggregate_result, aggregation_model, labelling_function, metric, datadoc, result
from rest_framework import serializers

class labelling_function_serializer(serializers.ModelSerializer):

    class Meta:
        model = labelling_function
        fields = ('__all__')

class labelling_function_results_serializer(serializers.ModelSerializer):

    class Meta:
        model = result
        fields = ['id', 'function']


class datadoc_serializer(serializers.ModelSerializer):

    class Meta:
        model = datadoc
        fields = ['project']

class aggregation_model_serializer(serializers.ModelSerializer):

    class Meta:
        model = aggregation_model
        fields = ['model_name', 'model_type', 'project', 'disabled_functions']

class aggregate_results_serializer(serializers.ModelSerializer):

    class Meta:
        model = aggregate_result
        fields = ['model_version','project'] #,'result']

class metrics_serializer(serializers.ModelSerializer):

    class Meta:
        model = metric
        fields = ['project']