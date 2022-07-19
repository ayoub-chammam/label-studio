from rest_framework import viewsets, mixins
from django.conf import settings
from rest_framework.response import Response

from .serializers import aggregate_results_serializer, aggregation_model_serializer, labelling_function_serializer, metrics_applier_serializer, weak_annotation_serializer, labelling_function_results_serializer
from .models import aggregate_result, aggregation_model, labelling_function, metric, result, weak_annotation_log
from tasks.models import Task
from .labelling_templates.string_templates import *

from skweak.gazetteers import GazetteerAnnotator, Trie
import spacy
from spacy.tokens import Doc
import skweak
from skweak.analysis import LFAnalysis

############################################ # crud labelling function ############################################
# Labelling Function CRUD
class labelling_functions_CRUD_API(viewsets.ModelViewSet):
    queryset = labelling_function.objects.all()
    serializer_class = labelling_function_serializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']


############################################ # create spacy docs ############################################
# Apply Spacy model to generate correspondant docs
class spacy_generator_API(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = weak_annotation_serializer
    queryset = weak_annotation_log.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        data = serializer.validated_data
        project = data['project']
        tasks = Task.objects.all().filter(project= project)
        try:
            uid = weak_annotation_log.objects.latest('id').id
        except:
            uid = 0
        objs = []
        for task in tasks:
            doc = nlp(task.data['text'])
            objs.append(
                weak_annotation_log(
                    id = uid + 1,
                    spacy_doc = doc.to_json(),
                    task = task,
                    project = project,
                    text = doc.text
                )
            )
            uid += 1
        weak_annotation_log.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)
        return Response({'status': 'OK'})


########################### # update spacy docs to include results from labelling function ##################################

# currently supports Gazetteers only
class labelling_function_logsAPI(viewsets.GenericViewSet, mixins.CreateModelMixin):

    serializer_class = labelling_function_results_serializer
    queryset = weak_annotation_log.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        function = serializer.validated_data['function']
        function_name = function.name
        label = function.label
        project = function.project
        keywords = function.content.split(',')
        keywords = [[element] for element in keywords]
        tries = {label: Trie(keywords)}

        tasks = Task.objects.all().filter(project_id= project)
        for task in tasks:
            doc = weak_annotation_log.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)

            skweak_gazetteer_function = GazetteerAnnotator(function_name, tries, case_sensitive=False)
            doc = skweak_gazetteer_function(doc)
            doc_json = doc.to_json()
            weak_annotation_log.objects.filter(task_id=task).update(spacy_doc=doc_json)
        return super().perform_create(serializer)

########################### # apply labelling function and save results in results ##################################
class lf_results_API(viewsets.GenericViewSet, mixins.CreateModelMixin):
    # this function would take as input a labeling function id and bulk_creates annotations generated 
    # by the labeling function into the results table 
    serializer_class = labelling_function_results_serializer
    queryset = result.objects.all()
    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        function = serializer.validated_data['function']
        function_name = function.name
        label = function.label
        project = function.project
        
        tasks = Task.objects.all().filter(project_id= project)
        try:
            uid = result.objects.latest('id').id
        except:
            uid = 0
        objs = [] 
        for task in tasks:
            doc = weak_annotation_log.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)
            ents = doc.spans.get(function_name)
            res = []
            for ent in ents:
                item = {"from_name": "label", "to_name": "text", "type": "labels", "value": {}}
                item['value'] = {"start": ent.start_char,
                    "end": ent.end_char,
                    "text": ent.text,
                    "labels": [ent.label_]
                    }
                res.append(item)

            objs.append(
                result(
                    id = uid + 1,
                    function = function,
                    project = project,
                    model_version = function.name,
                    result = res,
                    task = task,
                )
            )
            uid += 1
        result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)
        # return super().perform_create(serializer)


##################### # defining an aggregation model      ##################################
class aggregationModelAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = aggregation_model_serializer
    queryset = aggregation_model.objects.all()
    def perform_create(self, serializer):
        return super().perform_create(serializer)


##################### # update spacy docs to include aggregation results            ##################################
##################### # apply aggregate model and save results in aggregate_results ##################################

class aggregate_results_API(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = aggregate_results_serializer
    queryset = aggregate_result.objects.all()
    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        # collect parameters
        model_type = serializer.validated_data['model_type']
        model_name = serializer.validated_data['model_name']
        project = serializer.validated_data['project']
                
        tasks = Task.objects.all().filter(project_id= project)
        
        # Collect all docs into one list
        docs = []
        for task in tasks:
            doc = weak_annotation_log.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)
            docs.append(doc)
        
        # select aggregation model type and apply model
        if model_type == 'HMM':
            agg_model = skweak.aggregation.HMM(model_name,['PER', 'LOC', 'ORG', 'MISC'])
        elif model_type == 'Majority Voting':
            agg_model = skweak.aggregation.MajorityVoter(model_name,['PER', 'LOC', 'ORG', 'MISC'])
        
        docs = agg_model.fit_and_aggregate(docs)

        # check for valid ID insertion
        try:
            uuid = aggregate_result.objects.latest('id').id
        except:
            uuid = 0

        # iterate over docs, and extract annotations corresponding to aggreation model
        objs = []
        for doc in docs:
            ents = doc.spans.get(model_name)
            res = []
            taskid = weak_annotation_log.objects.get(text=doc.text).task_id
            for ent in ents:
                item = {"from_name": "label", "to_name": "text", "type": "labels", "value": {}}
                item['value'] = {"start": ent.start_char,
                    "end": ent.end_char,
                    "text": ent.text,
                    "labels": [ent.label_]
                    }
                res.append(item)
            
            # update spacy docs to include annotations of agg model
            doc_json = doc.to_json()
            weak_annotation_log.objects.filter(task_id=taskid).update(spacy_doc=doc_json)

            # save annotations of agg model to results table
            objs.append(
                aggregate_result(
                    id = uuid + 1,
                    model_name = model_name,
                    model_type = model_type,
                    annotation = res,
                    task = Task.objects.get(id=taskid),
                    project = task.project_id,
                )
            )
            uuid += 1
        
        # bulk save annotations of agg model
        aggregate_result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

        # return super().perform_create(serializer)

########################### # calculate metrics over spacy docs (coverage, conflicts, overlaps) ##################################
class metrics_calculatorAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = metrics_applier_serializer
    queryset = result.objects.all()
    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        project = serializer.validated_data['project']

        tasks = Task.objects.all().filter(project_id= project)

        # checking correct start id
        try:
            uuid = metric.objects.latest('id').id
        except:
            uuid = 0

        # getting docs
        docs = []
        for task in tasks:
            doc = weak_annotation_log.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)
            docs.append(doc)
        
        # applying analyser
        analyzer = LFAnalysis(docs,['PER','LOC', 'ORG', 'MISC'])

        print('---------------------------')      
        lf_names = list(labelling_function.objects.values_list('name', flat=True))
        model_names = list(aggregate_result.objects.values_list('model_name',flat=True).distinct())
        
        print(model_names)

        objs = []
        # getting scores into dicts
        overlaps = analyzer.lf_overlaps().to_dict()
        coverages = analyzer.lf_coverages().to_dict()
        conflicts = analyzer.lf_conflicts().to_dict()

        fcts = list(overlaps.keys())
        labels = ['PER','LOC','ORG','MISC']
        print(fcts)
        # getting scores
        for fct in fcts:
            for label in labels:
                if fct in lf_names:
                    objs.append(
                        metric(
                            id = uuid + 1,
                            project = project, function = labelling_function.objects.get(name=fct), label = label,
                            coverage = coverages[fct][label],
                            conflicts = conflicts[fct][label],
                            overlaps = overlaps[fct][label],
                        )
                    )
                    uuid += 1                    
                elif fct in model_names:
                    objs.append(
                        metric( 
                            id = uuid + 1,
                            project = project, model = aggregation_model.objects.get(model_name=fct), label = label,
                            coverage = coverages[fct][label],
                            conflicts = conflicts[fct][label],
                            overlaps = overlaps[fct][label],
                        )
                    )
                    uuid += 1
        metric.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

        return super().perform_create(serializer)
