from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api

app_name = "labelling_functions"

router = DefaultRouter()


# CRUD
router.register(r'', api.labelling_functions_CRUD_API, basename='CRUD_LF')

router.register(r'spacy_apply', api.spacy_generator_API, basename='spacy_apply')

_api_urlpatterns = router.urls


urlpatterns = [
    path('labelling_functions/', include((_api_urlpatterns, app_name), namespace='api_labelling_functions')),
]




# _api_urlpatterns = [
#     # CRUD
#     path('labelling_functions/', api.LabellingfunctionAPI.as_view(), name='LF-list'),
#     path('labelling_functions/<int:pk>/', api.LabellingFunction_RUD_API.as_view(), name='LF-detail'),

# ]
