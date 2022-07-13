from rest_framework import viewsets, mixins
from django.conf import settings
from rest_framework.response import Response

from .serializers import labelling_function_serializer, weak_annotation_serializer, labelling_function_results_serializer
from .models import labelling_function, weak_annotation_logs
from tasks.models import Task
from .labelling_templates.string_templates import *

from skweak.gazetteers import GazetteerAnnotator, Trie
import spacy
from spacy.tokens import Doc


# Labelling Function CRUD
class labelling_functions_CRUD_API(viewsets.ModelViewSet):
    queryset = labelling_function.objects.all()
    serializer_class = labelling_function_serializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']


# Apply Spacy model to generate correspondant docs
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









from rest_framework import generics
class labelling_function_logsAPI(viewsets.GenericViewSet, mixins.CreateModelMixin):
    # generics.CreateAPIView):
    # mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = labelling_function_results_serializer
    queryset = weak_annotation_logs.objects.all()


    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        # function_name = serializer.validated_data['name']
        function = serializer.validated_data['function']
        function_name = function.name
        #function = labelling_function.objects.filter(name=function_name)
        print(function)
        label = function.label
        project = function.project
        keywords = function.content.split(',')
        keywords = [[element] for element in keywords]
        tries = {label: Trie(keywords)}

        tasks = Task.objects.all().filter(project_id= project)


        for task in tasks:
            doc = weak_annotation_logs.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)

            skweak_gazetteer_function = GazetteerAnnotator(function_name, tries, case_sensitive=False)
            doc = skweak_gazetteer_function(doc)
            doc_json = doc.to_json()
            weak_annotation_logs.objects.filter(task_id=task).update(spacy_doc=doc_json)

        return super().perform_create(serializer)



# class LabellingfunctionAPI(generics.ListCreateAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer


# class LabellingFunction_RUD_API(generics.RetrieveUpdateDestroyAPIView):
#     queryset = labelling_function.objects.all()
#     serializer_class = labelling_function_serializer