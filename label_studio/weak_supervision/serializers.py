from .models import SpacyModel, Modelmetric, SpacyModelMetric, SpacyModelResult, aggregate_result, aggregation_model, labelling_function, LFmetric, datadoc, result
from rest_framework import serializers

############################################################################
####################### Labelling Function Serializers #####################
############################################################################

class SpacyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpacyModel
        fields = ('__all__')
class SpacyModelApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpacyModelResult
        fields = ['id', 'model']
class SpacyModelMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpacyModelMetric
        fields = ['project', 'model']


class GazetteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = labelling_function
        fields = ('id', 'name', 'file_path', 'label', 'type', 'project')


class LFSerializer(serializers.ModelSerializer):
    class Meta:
        model = labelling_function
        #fields = ('__all__')
        fields = ('id', 'name', 'label', 'type', 'content', 'project',
                  'created_at', 'updated_at', 'precision', 'recall', 'f1_score', 'coverage', 'overlap', 'conflict')


class LFApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = result
        fields = ['id', 'function']


class LFResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = result
        fields = ('__all__')


class LFMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = LFmetric
        fields = ['project']


class LFMetricResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LFmetric
        fields = ('__all__')


############################################################################
class DataDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = datadoc
        fields = ['project']
############################################################################


############################################################################
####################### Aggregation Model Serializers ######################
############################################################################

class AggModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = aggregation_model
        fields = ('__all__')


class AggModelApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = aggregate_result
        fields = ['model', 'project']


class AggModelResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = aggregate_result
        fields = ('__all__')


class AggModelMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelmetric
        fields = ['project', 'model']


class AggModelMetricResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelmetric
        fields = ('__all__')
