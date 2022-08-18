from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling functions"

router = DefaultRouter()


router.register(r'docs', api.SpaCyGeneratorAPI, basename='spacy-apply')

router.register(r'labelling_functions', api.LFCRUDAPI, basename='LF-CRUD')

router.register(r'lf_annotate', api.LFAnnotationAPI, basename='run-function')

router.register(r'agg_model', api.AggModelAPI, basename='Model-CRUD') # TODO:UpdateDelete

router.register(r'agg_model_annotate', api.AggModelAnnotationAPI, basename='agg-apply')

router.register(r'lf_metrics', api.LFmetricsAPI, basename='generate-lf-metrics')

router.register(r'agg_model_metrics', api.ModelmetricsAPI, basename='generate-model-metrics')

_api_LFs_urlpatterns = router.urls


urlpatterns = [
    path('weak/', include((_api_LFs_urlpatterns, app_name), namespace='api-LFs')),

    path('weak/labelling_functions/project', api.ProjectLFsAPI.as_view(), name="project-lfs"),
    path('weak/labelling_functions/label', api.LabelLFsAPI.as_view(), name="label-lfs"),
    path('weak/lf_annotate/annotations', api.LFResultsAPI.as_view(), name="lf-results"),
    path('weak/lf_metrics/scores', api.GetLFmetricsAPI.as_view(), name="lf-metrics"),

    path('weak/agg_model/project', api.ProjectModelsAPI.as_view(), name="project-models"),
    path('weak/agg_model/annotations', api.ModelResultsAPI.as_view(), name="model-results"),
    path('weak/agg_model/scores', api.GetModelmetricsAPI.as_view(), name="model-metrics"),

]
