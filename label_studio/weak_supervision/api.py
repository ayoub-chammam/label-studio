from django.conf import settings
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from projects.models import Project
from tasks.models import Prediction

from tasks.models import Task
from .models import LFmetric, aggregate_result, aggregation_model, labelling_function, result, datadoc
from .serializers import *
# aggregate_results_serializer, aggregation_model_serializer, labelling_function_serializer, datadoc_serializer, labelling_function_results_serializer, metrics_serializer

from .utils import *
# get_keywords_from_content, get_latest_idx, get_lf_results, gold_preds_to_spans, scores_to_json
from .templates.string_templates import *

import spacy
import skweak
from spacy.tokens import Doc
from skweak.heuristics import RegexAnnotator, FunctionAnnotator
from skweak.gazetteers import GazetteerAnnotator, Trie
from skweak.analysis import LFAnalysis
from skweak import aggregation



############################################ # crud labelling function ############################################
# Labelling Function CRUD
class LabellingFunctionsAPI(viewsets.ModelViewSet):
    queryset = labelling_function.objects.all()
    serializer_class = labelling_function_serializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

############################################ # create spacy docs ############################################
# Apply Spacy model to generate correspondant docs
class spacy_generator_API(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = datadoc_serializer
    queryset = datadoc.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        data = serializer.validated_data
        project = data['project']
        tasks = Task.objects.all().filter(project= project)

        uid = get_latest_idx(datadoc)

        objs = []
        for task in tasks:
            doc = nlp(task.data['text'])
            # getting gold labels
            try:
                gold_preds = Prediction.objects.get(task=task, model_version='gold').result
                doc = gold_preds_to_spans(doc, gold_preds)
            except:
                # No GT for the data
                print('No Ground Truth available')
                pass
            objs.append(
                datadoc(id = uid + 1, project = project, task = task, text = doc.text, spacy_doc = doc.to_json())
            )
            uid += 1
        datadoc.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)
        return Response({'status': 'OK'})


############################## apply LF and save results ####################################################
class LFAnnotationAPI(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = labelling_function_results_serializer
    queryset = result.objects.all()
    
    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        function = serializer.validated_data['function']
        function_name = function.name
        label = function.label
        project = function.project
        content = function.content

        tasks = Task.objects.all().filter(project_id= project)
        uid = get_latest_idx(result)

        # define LF from keywords matching list
        if function.type == 1:
            tries = get_keywords_from_content(content, label)
            print(tries)
            annotator = GazetteerAnnotator(function_name, tries)

        # define LF from regex expression
        elif function.type == 2:
            annotator = RegexAnnotator(function_name, content, label)

        # define LF from Python Script
        elif function.type == 3:
            script = content
            exec(script)
            _locals = locals()
            LF = _locals.get(function_name)
            annotator = FunctionAnnotator(function_name, LF)

        # Apply LF on Project Tasks
        objs = []    
        for task in tasks:
            doc = datadoc.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)

            doc = annotator(doc)
            doc_json = doc.to_json()
            datadoc.objects.filter(task_id=task).update(spacy_doc=doc_json)
            res = get_lf_results(doc, function_name)
            print(res)
            if res:
                objs.append(
                    result(
                        id = uid + 1,
                        function = function,
                        project = project,
                        model_version = function.name,
                        label = label,
                        result = res,
                        task = task,
                    )
                )
                uid += 1
        result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)
        return Response({'status': 'OK'})
        

##################### # defining an aggregation model      ##################################
class aggregationModelAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = aggregation_model_serializer
    queryset = aggregation_model.objects.all()
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        labels = project.control_weights["label"]["labels"]
        serializer.validated_data['labels'] = labels
        serializer.is_valid()
        # serializer.save()
        return super().perform_create(serializer)


##################### # apply aggregate model  ##################################
class aggregate_results_API(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    
    serializer_class = aggregate_results_serializer
    queryset = aggregate_result.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        # collect parameters
        model = serializer.validated_data['model_version']
        model_name = model.model_name
        model_type = model.model_type

        # get_initial_weights
        weights = model.get_initial_weights()

        project = serializer.validated_data['project']

        labels = model.get_labels()
        docs = datadoc.get_project_docs(project)
        weights = remove_gold(docs, weights)

        # select aggregation model type and apply model
        if model_type == 'HMM':
            agg_model = aggregation.HMM(model_name,labels, initial_weights=weights)
        elif model_type == 'Majority Voting':
            agg_model = aggregation.MajorityVoter(model_name,labels, initial_weights=weights)

        docs = agg_model.fit_and_aggregate(docs)

        # check for valid ID insertion
        uid = get_latest_idx(aggregate_result)
        # iterate over docs, and extract annotations corresponding to aggreation model
        objs = []
        for doc in docs:
            taskid = datadoc.objects.get(text=doc.text, project=project).task_id
            doc_json = doc.to_json()
            datadoc.objects.filter(task_id=taskid).update(spacy_doc=doc_json)
            res = get_lf_results(doc, model_name)
            
            # save annotations of agg model to results table
            objs.append(
                aggregate_result(
                    id = uid + 1,
                    model_version = model,
                    project = project,
                    task = Task.objects.get(id=taskid),
                    result = res,
                )
            )
            uid += 1
        
        aggregate_result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)


class LFmetricsAPI(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = metrics_serializer
    queryset = LFmetric.objects.all()

    def perform_create(self, serializer):

        project = serializer.validated_data['project']
        docs = datadoc.get_project_docs(project)
        labels = Project.get_project_labels(project)
        
        # get function name
        LF_names = labelling_function.get_lf_names()

        labelling_function_scores = lf_scores(docs, labels, LF_names)
        print(labelling_function_scores)

        uid = get_latest_idx(LFmetric)
        objs = []
        for fct in LF_names:
            for score in labelling_function_scores:
                # print(score)
                # if check_gold(docs):

                #     objs.append(
                #         LFmetric(
                #         id = uid + 1, project=project,
                #         function = labelling_function.objects.get(name=score['annotator']),
                #         label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                #         overlaps=score['overlaps'], precision=score['precision'], recall=score['recall'], 
                #         f1_score=score['f1'],
                #         )
                #     )
                #     uid += 1 
                # else:                   
                objs.append(
                    LFmetric(
                    id = uid + 1, project=project,
                    function = labelling_function.objects.get(name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'],
                    )
                )
                uid += 1 
        LFmetric.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

        return super().perform_create(serializer)

########################### # calculate metrics over spacy docs (coverage, conflicts, overlaps) ##################################
class ModelmetricsAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = aggregation_model_serializer
    queryset = aggregation_model.objects.all()
    def perform_update(self, serializer):

        project = serializer.validated_data['project']
        docs = datadoc.get_project_docs(project)
        labels = project.get_project_labels()
        model_name = serializer.validated_data['model_name']
        agg_model_scores = model_scores(docs,labels,model_name)

        serializer.validated_data['labels'] = labels
        print(agg_model_scores)

        serializer.is_valid()
        # serializer.save()
        return super().perform_update(serializer)

        
##########################################################
# One API post request 
# calculates metrics from ground truth
# check for labeling function   if function name in lf_names then add it
# bulk update labelling functions with function name = function name