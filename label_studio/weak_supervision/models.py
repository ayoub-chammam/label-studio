from django.db import models
from projects.models import Project
from tasks.models import Task
from django.utils.translation import gettext_lazy as _
import spacy
from spacy.tokens import Doc

class SpacyModel(models.Model):
    name = models.CharField(
        max_length=60, help_text='name of the ner model', unique=True)
    path = models.CharField(
        max_length=60, help_text='name of the ner model')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    labels = models.JSONField('list of labels', default=None)
    
    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time an aggreagation model was created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time an aggreagation model was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)

class SpacyModelResult(models.Model):
    model = models.ForeignKey(
        SpacyModel, on_delete=models.CASCADE, help_text='labelling function ID')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, help_text='Task ID')
    result = models.TextField(null=True)
    model_version = models.TextField('model_version', null=True)

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a model annotation is created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a model annotation was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)

class SpacyModelMetric(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')

    model = models.ForeignKey(
        SpacyModel, on_delete=models.CASCADE, help_text='ner model ID', null=True)

    label = models.CharField(max_length=60, null=True,
                             help_text='label')

    coverage = models.FloatField(blank=True, null=True, default=0.0)
    conflicts = models.FloatField(blank=True, null=True, default=0.0)
    overlaps = models.FloatField(blank=True, null=True, default=0.0)

    precision = models.FloatField(blank=True, null=True, default=0.0)
    recall = models.FloatField(blank=True, null=True, default=0.0)
    f1_score = models.FloatField(blank=True, null=True, default=0.0)

    results = models.IntegerField(blank=True, null=True, default=0.0)

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a metric was calculated')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a metric was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["model", "label"], name='ner-model-label')
    ]

class labelling_function(models.Model):
    """
    Labelling Function class used for automatic data labeling in weak supervision
    """
    file_path = models.FileField(null=True)
    templates = (
        (1, _('all matches of one or a list of keywords')),
        # Example: Google, Apple, Amazon,  Heartex Inc, etc.

        (2, _('all matches of a regex pattern')),
        # Uploaded Gazetteer in JSON File:
        # Example: {"COMPANY": ['Apple', 'Google', 'EY']}

        (3, _('all matches of a regex pattern')),
        # Example: (?:Mr\.|Mrs\.) [a-zA-Z]+

        (4, _('a script of a python function')),
        # Example: def factorial(num):\n\tfact=1\n\tfor i in range(1,num+1):\n\t\tfact = fact*i\n\treturn fact\nprint(factorial(3))
    )

    name = models.CharField(
        max_length=60, help_text='name of the Labelling Function', unique=True)
    label = models.CharField(
        max_length=60, help_text='Label Attributed for the Labelling Function')
    type = models.IntegerField(
        choices=templates, default=None)
    content = models.TextField(
        default='', null=True, help_text='Searched Word or Regular expression to match - '
        'in Text corresponding to selected label or LF with Python code')
    project = models.ForeignKey(
        Project, related_name='project', on_delete=models.CASCADE, null=True,
        help_text='Project ID where the Labelling Function is created')

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a labelling function was created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a labelling function was updated')

    precision = models.FloatField(
        _('precision'), default=None, help_text='LF Precision score', null=True)
    recall = models.FloatField(
        _('recall'), default=None, help_text='LF Recall score', null=True)
    f1_score = models.FloatField(
        _('f1_score'), default=None, help_text='LF F_score score', null=True)
    coverage = models.FloatField(
        _('coverage'), default=None, help_text='LF Coverage score', null=True)
    overlap = models.FloatField(
        _('overlap'), default=None, help_text='LF Overlap score', null=True)
    conflict = models.FloatField(
        _('conflict'), default=None, help_text='LF Conflict score', null=True)

    def __str__(self):
        return self.name

    def has_permission(self, user):
        return self.project.has_permission(user)

    def get_lf_names():
        names = list(labelling_function.objects.all(
        ).values_list('name', flat=True))
        return names


class datadoc(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    #task = models.ForeignKey(Task, on_delete=models.CASCADE, unique=True, help_text='Task ID')
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, help_text='Task ID')
    text = models.TextField(
        default=None, null=True, help_text='Corresponding text')
    spacy_doc = models.JSONField(
        'doc', default=None, help_text='SpaCy doc file relative to each Task in JSON Format')

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a spacy model was run')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a spacy annotation was updated (added spans)')

    def has_permission(self, user):
        return self.project.has_permission(user)

    @classmethod
    def get_project_docs(self, project):
        docs = list(datadoc.objects.filter(
            project=project).values_list('spacy_doc', flat=True))
        nlp = spacy.load('en_core_web_sm')
        for idx, doc in enumerate(docs):
            docs[idx] = Doc(nlp.vocab).from_json(doc)
        return docs


class result(models.Model):
    function = models.ForeignKey(
        labelling_function, on_delete=models.CASCADE, help_text='labelling function ID')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, help_text='Task ID')

    result = models.TextField(null=True)
    label = models.CharField(
        max_length=60, null=True, help_text='label of the entity')

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a labelling function annotation is created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a labelling function annotation was updated')

    model_version = models.TextField('labeling_function', null=True)
    final = models.BooleanField('final model', null=True)


    def has_permission(self, user):
        return self.project.has_permission(user)


class aggregation_model(models.Model):
    templates = (
        ('HMM', _('hidden markov model')),
        ('Majority Voting', _('Majroity Voting')),
    )
    model_name = models.CharField(
        max_length=60, help_text='name of the aggregation model')
    model_type = models.CharField(choices=templates, max_length=60)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    labels = models.JSONField('list of labels', default=None)
    
    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time an aggreagation model was created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time an aggreagation model was updated')

    disabled_functions = models.ManyToManyField(
        'labelling_function', blank=True,
        related_name='LFs',
        help_text='selected labelling functions to ignore for the agg. model',
    )

    precision = models.FloatField(
        _('precision'), help_text='agg model Precision score', null=True, default=0.0)
    recall = models.FloatField(
        _('recall'), help_text='agg model Recall score', null=True, default=0.0)
    f1_score = models.FloatField(
        _('f1_score'), help_text='agg model F_score score', null=True, default=0.0)
    coverage = models.FloatField(
        _('coverage'), help_text='agg model Coverage score', null=True, default=0.0)
    overlaps = models.FloatField(
        _('overlap'), help_text='agg model Overlap score', null=True, default=0.0)
    conflicts = models.FloatField(
        _('conflict'), help_text='agg model Conflict score', null=True, default=0.0)

    def has_permission(self, user):
        return self.project.has_permission(user)

    def get_labels(self):
        return list(self.labels)

    def get_initial_weights(self):
        fcts = self.disabled_functions.all()
        names = list(fcts.values_list('name', flat=True))
        weights = {fct: 0 for fct in names}
        return weights

    def get_model_names():
        names = list(labelling_function.objects.all(
        ).values_list('model_name', flat=True))
        return names

class aggregate_result(models.Model):

    model = models.ForeignKey(
        aggregation_model, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, help_text='Task ID')
    result = models.TextField(null=True, help_text='annotation results')

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time an aggreagtion model annotation was created')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time an aggregation model annotation was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)


class LFmetric(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')

    function = models.ForeignKey(
        labelling_function, on_delete=models.CASCADE, help_text='labelling function ID', null=True)

    label = models.CharField(max_length=60, null=True,
                             help_text='label')

    coverage = models.FloatField(blank=True, null=True, default=0.0)
    conflicts = models.FloatField(blank=True, null=True, default=0.0)
    overlaps = models.FloatField(blank=True, null=True, default=0.0)

    precision = models.FloatField(blank=True, null=True, default=0.0)
    recall = models.FloatField(blank=True, null=True, default=0.0)
    f1_score = models.FloatField(blank=True, null=True, default=0.0)

    results = models.IntegerField(blank=True, null=True, default=0.0)

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a metric was calculated')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a metric was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["function", "label"], name='function-label')
    ]

class Modelmetric(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, help_text='Project ID')

    model = models.ForeignKey(
        aggregation_model, on_delete=models.CASCADE, help_text='agg model ID', null=True)

    label = models.CharField(max_length=60, null=True,
                             help_text='label')

    coverage = models.FloatField(blank=True, null=True, default=0.0)
    conflicts = models.FloatField(blank=True, null=True, default=0.0)
    overlaps = models.FloatField(blank=True, null=True, default=0.0)

    precision = models.FloatField(blank=True, null=True, default=0.0)
    recall = models.FloatField(blank=True, null=True, default=0.0)
    f1_score = models.FloatField(blank=True, null=True, default=0.0)

    results = models.IntegerField(blank=True, null=True, default=0.0)

    created_at = models.DateTimeField(
        _('created at'), auto_now_add=True, help_text='Time a metric was calculated')
    updated_at = models.DateTimeField(
        _('updated at'), auto_now=True, help_text='Last time a metric was updated')

    def has_permission(self, user):
        return self.project.has_permission(user)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["model", "label"], name='model-label')
    ]