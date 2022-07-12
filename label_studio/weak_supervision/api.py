from rest_framework import viewsets, mixins

from .serializers import labelling_function_serializer, weak_annotation_serializer
from .models import labelling_function, weak_annotation_logs
from .labelling_templates.string_templates import *

import spacy
from tasks.models import Task
from django.conf import settings
from rest_framework.response import Response


class labelling_functions_CRUD_API(viewsets.ModelViewSet):
    queryset = labelling_function.objects.all()
    serializer_class = labelling_function_serializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']



class spacy_generator_API(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = weak_annotation_serializer
    queryset = weak_annotation_logs.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        data = serializer.validated_data
        project = data['project']
        tasks = Task.objects.all().filter(project= project)
        try:
            uid = weak_annotation_logs.objects.latest('id').id
        except:
            uid = 0
        objs = []
        for task in tasks:
            doc = nlp(task.data['text'])
            objs.append(
                weak_annotation_logs(
                    id = uid + 1,
                    spacy_doc = doc.to_json(),
                    task = task,
                    project = project,
                )
            )
            uid += 1
        weak_annotation_logs.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

        return Response({'status': 'OK'})






# class LabellingfunctionAPI(generics.ListCreateAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer


# class LabellingFunction_RUD_API(generics.RetrieveUpdateDestroyAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer