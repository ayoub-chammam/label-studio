from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling functions"

router = DefaultRouter()


router.register(r'docs', api.spacy_generator_API, basename='spacy-apply')

router.register(r'labellingfunctions', api.LabellingFunctionsAPI, basename='LF-CRUD')

router.register(r'apply_LF', api.LFAnnotationAPI, basename='run-function')

router.register(r'model', api.aggregationModelAPI, basename='Model-CRUD') # TODO:UpdateDelete

router.register(r'apply_model', api.aggregate_results_API, basename='agg-apply')

router.register(r'calculate_lf_metrics', api.LFmetricsAPI, basename='generate-lf-metrics')

router.register(r'calculate_model_metrics', api.ModelmetricsAPI, basename='generate-model-metrics')

_api_LFs_urlpatterns = router.urls


urlpatterns = [
    path('weak/', include((_api_LFs_urlpatterns, app_name), namespace='api-LFs')),
]