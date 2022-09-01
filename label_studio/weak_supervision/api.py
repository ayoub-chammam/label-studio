from django.conf import settings
from rest_framework import generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from projects.models import Project
from tasks.models import Prediction, Task

from .models import *
from .serializers import *
from .utils import *

import spacy
import skweak
from spacy.tokens import Doc
from skweak.heuristics import RegexAnnotator, FunctionAnnotator
from skweak.gazetteers import GazetteerAnnotator
from skweak import aggregation

from .filters import *
import re



############################################################################
####################### Labelling Function Views  ##########################
############################################################################
        
class SpacyModelCRUDAPI(viewsets.ModelViewSet):
    queryset = SpacyModel.objects.all()
    serializer_class = SpacyModelSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
class SpacyModelAnnotationAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):

    serializer_class = SpacyModelApplySerializer
    queryset = SpacyModelResult.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        ner_model = serializer.validated_data['model']
        model_name = ner_model.name
        model_path = ner_model.path
        project = ner_model.project
        labels = project.get_project_labels()
        # response = super().perform_create(serializer)
        # ner_model = labelling_function.objects.get(name=model_name)

        annotator = skweak.spacy.ModelAnnotator(model_name, model_path)
        ### Getting Project Tasks
        tasks = Task.objects.all().filter(project_id= project)
        uid = get_latest_idx(SpacyModelResult)
        
        ### Applying Gazetteer on Project Tasks
        objs = []    
        for task in tasks:
            doc = datadoc.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)
            doc = annotator(doc)
            # Standarize labels to conll format
            print(doc.spans.data)
            doc = ConLL2003Standardiser(doc)
            ents = doc.spans.get(model_name)
            for ent in ents:
                print(ent, ent.label_)
            
            doc_json = doc.to_json()
            # Update Docs
            datadoc.objects.filter(task_id=task).update(spacy_doc=doc_json)
            # get 
            res = get_lf_results(doc, model_name)
            print(res)
            if res:
                objs.append(
                    SpacyModelResult(
                        id = uid + 1,
                        model = ner_model,
                        project = project,
                        model_version = ner_model.name,
                        result = res,
                        task = task,
                    )
                )
                uid += 1
        # Save Results
        SpacyModelResult.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)


        return super().perform_create(serializer)

class SpacyModelMetricsAPI(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SpacyModelMetricSerializer
    queryset = SpacyModelMetric.objects.all()
    
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        docs = datadoc.get_project_docs(project)
        labels = project.get_project_labels()
        model = serializer.validated_data['model'].name
        agg_model_scores = model_scores(docs,labels,model)

        uid = get_latest_idx(SpacyModelMetric)
        objs = []
        for score in agg_model_scores:
            if 'precision' in score.keys():
                objs.append(
                    SpacyModelMetric(
                    id = uid + 1, project=project,
                    model = SpacyModel.objects.get(name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'], precision=score['precision'], recall=score['recall'], 
                    f1_score=score['f1'],
                    )
                )
                uid += 1 
            else:                   
                objs.append(
                    SpacyModelMetric(
                    id = uid + 1, project=project,
                    model = SpacyModel.objects.get(name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'],
                    )
                )
                uid += 1 
        return SpacyModelMetric.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)
    
############################################ # crud labelling function ############################################
class LFCRUDAPI(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser,)
    queryset = labelling_function.objects.all()
    serializer_class = LFSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

############################################ # Gazetteer Labelling Function ############################################
class LFGazetterAPI(mixins.CreateModelMixin, viewsets.GenericViewSet):
    parser_classes = (MultiPartParser,)
    queryset = labelling_function.objects.all()
    serializer_class = GazetteerSerializer

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        function_name = serializer.validated_data['name']
        label = serializer.validated_data['label']
        project = serializer.validated_data['project']
        file_path = serializer.validated_data['file_path']

        # Save LF
        response = super().perform_create(serializer)
        function = labelling_function.objects.get(name=function_name)
        print(function.id)

        ### Applying Gazetteer Function
        tries = skweak.gazetteers.extract_json_data(file_path.temporary_file_path())
        annotator = GazetteerAnnotator(function_name, tries)

        ### Getting Project Tasks
        tasks = Task.objects.all().filter(project_id= project)
        uid = get_latest_idx(result)
        
        ### Applying Gazetteer on Project Tasks
        objs = []    
        for task in tasks:
            doc = datadoc.objects.get(task_id=task).spacy_doc
            doc = Doc(nlp.vocab).from_json(doc)

            doc = annotator(doc)
            doc_json = doc.to_json()
            # Update Docs
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
        # Save Results
        result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)


class ProjectLFsAPI(generics.ListAPIView):
    search_fields = ['=project__id']
    filter_backends = [ProjectSearchFilter]
    queryset = labelling_function.objects.all()
    serializer_class = LFSerializer

class LabelLFsAPI(generics.ListAPIView):
    search_fields = ['=label']
    filter_backends = [LabelSearchFilter]
    queryset = labelling_function.objects.all()
    serializer_class = LFSerializer    

############################## apply LF and save results ####################################################
class LFAnnotationAPI(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = LFApplySerializer
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

        # define LF from gazetteer json file
        if function.type == 2:
            gazetter = str(function.file_path)
            tries = skweak.gazetteers.extract_json_data(gazetter)
            print(tries)
            annotator = GazetteerAnnotator(function_name, tries)

        # define LF from regex expression
        elif function.type == 3:
            annotator = RegexAnnotator(function_name, content, label)

        # define LF from Python Script
        elif function.type == 4:
            script = content
            print(script)
            print('--------------', len(script))
            print(script[-1])
            L = [script]
            print(L)
            script2 = script.replace('\\n', '\n').replace('\\t', '\t')
            print(script2)
            L2 = [script2]
            print(L2)
            # script3 = "def legal(doc):\n\tfor chunk in doc.noun_chunks:\n\t\tif chunk[-1].text.lower() in ['ltd', 'inc', 'sa']:\n\t\t\tyield chunk.start, chunk.end, 'ORG'"
            # print(script3)
            exec(script2)
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

class LFResultsAPI(generics.ListAPIView):
    search_fields = ['=function__id']
    filter_backends = [LFSearchFilter]
    queryset = result.objects.all()
    serializer_class = LFResultSerializer  

############################################ # create spacy docs ############################################
class SpaCyGeneratorAPI(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = DataDocSerializer
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

########################### # calculate metrics of labelling function ##################################
class LFmetricsAPI(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LFMetricSerializer
    queryset = LFmetric.objects.all()

    def perform_create(self, serializer):

        project = serializer.validated_data['project']
        docs = datadoc.get_project_docs(project)
        labels = Project.get_project_labels(project)
        
        # get function name
        LF_names = labelling_function.get_lf_names()

        labelling_function_scores = lf_scores(docs, labels, LF_names)

        uid = get_latest_idx(LFmetric)
        objs = []
        for score in labelling_function_scores:
            if 'precision' in score.keys():
                objs.append(
                    LFmetric(
                    id = uid + 1, project=project,
                    function = labelling_function.objects.get(name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'], precision=score['precision'], recall=score['recall'], 
                    f1_score=score['f1'],
                    )
                )
                uid += 1 
            else:                   
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


class GetLFmetricsAPI(generics.ListAPIView):
    search_fields = ['=function__id']
    filter_backends = [LFSearchFilter]
    queryset = LFmetric.objects.all()
    serializer_class = LFMetricResultSerializer    



############################################################################
####################### Aggregation Model Views  ###########################
############################################################################

##################### # defining an aggregation model  ##################################
class AggModelAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = AggModelSerializer
    queryset = aggregation_model.objects.all()
    
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        labels = project.control_weights["label"]["labels"]
        serializer.validated_data['labels'] = labels
        serializer.is_valid()
        return super().perform_create(serializer)

class ProjectModelsAPI(generics.ListAPIView):
    search_fields = ['=project__id']
    filter_backends = [ProjectSearchFilter]
    queryset = labelling_function.objects.all()
    serializer_class = AggModelSerializer

##################### # apply aggregate model  ##################################
class AggModelAnnotationAPI(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = AggModelApplySerializer
    queryset = aggregate_result.objects.all()

    def perform_create(self, serializer):
        nlp = spacy.load('en_core_web_sm')
        # collect parameters
        model = serializer.validated_data['model']
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
                    model_id = model,
                    project = project,
                    task = Task.objects.get(id=taskid),
                    result = res,
                )
            )
            uid += 1
        
        aggregate_result.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

class ModelResultsAPI(generics.ListAPIView):
    search_fields = ['=model__id']
    filter_backends = [ModelSearchFilter]
    queryset = aggregate_result.objects.all()
    serializer_class = AggModelResultSerializer  

########################### # calculate metrics of aggregation model ##################################
class ModelmetricsAPI(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = AggModelMetricSerializer
    queryset = Modelmetric.objects.all()
    
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        docs = datadoc.get_project_docs(project)
        labels = project.get_project_labels()
        model = serializer.validated_data['model'].model_name
        agg_model_scores = model_scores(docs,labels,model)

        uid = get_latest_idx(LFmetric)
        objs = []
        for score in agg_model_scores:
            if 'precision' in score.keys():
                objs.append(
                    Modelmetric(
                    id = uid + 1, project=project,
                    model = aggregation_model.objects.get(model_name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'], precision=score['precision'], recall=score['recall'], 
                    f1_score=score['f1'],
                    )
                )
                uid += 1 
            else:                   
                objs.append(
                    Modelmetric(
                    id = uid + 1, project=project,
                    model = aggregation_model.objects.get(model_name=score['annotator']),
                    label=score['label'], coverage=score['coverage'], conflicts=score['conflicts'],
                    overlaps=score['overlaps'],
                    )
                )
                uid += 1 
        return Modelmetric.objects.bulk_create(objs, batch_size=settings.BATCH_SIZE)

class GetModelmetricsAPI(generics.ListAPIView):
    search_fields = ['=model__id']
    filter_backends = [ModelSearchFilter]
    queryset = Modelmetric.objects.all()
    serializer_class = AggModelMetricResultSerializer   