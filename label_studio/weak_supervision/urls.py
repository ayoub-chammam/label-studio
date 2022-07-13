from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling functions"

router = DefaultRouter()


# CRUD
router.register(r'creator', api.labelling_functions_CRUD_API, basename='CRUD_LF')

router.register(r'applier', api.labelling_function_logsAPI, basename='function_apply')
router.register(r'doc_applier', api.spacy_generator_API, basename='spacy_apply')


_api_LFs_urlpatterns = router.urls


urlpatterns = [
    path('labeling_functions/', include((_api_LFs_urlpatterns, app_name), namespace='api-LFs')),

]



# _api_urlpatterns = [
#     # CRUD
#     path('labelling_functions/', api.LabellingfunctionAPI.as_view(), name='LF-list'),
#     path('labelling_functions/<int:pk>/', api.LabellingFunction_RUD_API.as_view(), name='LF-detail'),

# ]
