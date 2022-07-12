from rest_framework import viewsets, mixins

from .serializers import labelling_function_serializer
from .models import labelling_function
from .labelling_templates.string_templates import *


class labelling_functions_CRUD_API(viewsets.ModelViewSet):
    queryset = labelling_function.objects.all()
    serializer_class = labelling_function_serializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']











# class LabellingfunctionAPI(generics.ListCreateAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer


# class LabellingFunction_RUD_API(generics.RetrieveUpdateDestroyAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer