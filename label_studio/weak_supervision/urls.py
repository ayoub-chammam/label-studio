from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling functions"

router = DefaultRouter()


# CRUD
router.register(r'create_LF', api.labelling_functions_CRUD_API, basename='CRUD_LF')

router.register(r'apply_LF', api.labelling_function_logsAPI, basename='function_apply')

router.register(r'create_docs', api.spacy_generator_API, basename='spacy_apply')

router.register(r'store_LF_res', api.lf_results_API, basename='lf_results')

router.register(r'create_agg_model', api.aggregationModelAPI, basename='CRUD_agg') # TODO:UD

router.register(r'apply_agg_model', api.aggregate_results_API, basename='agg_apply')

router.register(r'calculate_metrics', api.metrics_calculatorAPI, basename='generate-metrics')



_api_LFs_urlpatterns = router.urls


urlpatterns = [
    path('weak/', include((_api_LFs_urlpatterns, app_name), namespace='api-LFs')),

]



# _api_urlpatterns = [
#     # CRUD
#     path('labelling_functions/', api.LabellingfunctionAPI.as_view(), name='LF-list'),
#     path('labelling_functions/<int:pk>/', api.LabellingFunction_RUD_API.as_view(), name='LF-detail'),

# ]
