from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling functions"

router = DefaultRouter()


# CRUD
router.register(r'docs', api.spacy_generator_API, basename='spacy-apply')

router.register(r'labellingfunctions', api.LabellingFunctionsAPI, basename='LF-CRUD')

router.register(r'apply_LF', api.LFAnnotationAPI, basename='run-function')

router.register(r'model', api.aggregationModelAPI, basename='Model-CRUD') # TODO:UpdateDelete

router.register(r'apply_model', api.aggregate_results_API, basename='agg-apply')

router.register(r'calculate_metrics', api.metricsAPI, basename='generate-metrics')

_api_LFs_urlpatterns = router.urls


urlpatterns = [
    path('weak/', include((_api_LFs_urlpatterns, app_name), namespace='api-LFs')),

]


# router.register(r'store_LF_res', api.lf_results_API, basename='lf_results') # TobeRemoved
