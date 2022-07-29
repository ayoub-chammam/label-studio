from email.policy import default
from django.db import models
from projects.models import Project
from tasks.models import Task
from django.utils.translation import gettext_lazy as _
import spacy
from spacy.tokens import Doc

# Create your models here.
# blank=True, default=''

class labelling_function(models.Model):
    """
    Labelling Function class used for automatic data labeling in weak supervision
    ------------------------------------------------------------------------------

     THINGS TO CONSIDER WHILE WRTINING A PYTHON SCRIPT FUNCTION:
    function must yield start, end, label and takes as input spacy doc file
    \n creates new line and 
    \t replaces the tab character
    Therefore writing the above function can be written in the following format:
    
    "def factorial(num):\n\tfact=1\n\tfor i in range(1,num+1):\n\t\tfact = fact*i\n\treturn fact\nprint(factorial(3))"

    """

    templates = (
       ('single_regex', _('first match of a regex pattern')),
       ('regex_matches', _('all matches of a regex pattern')),
       ('string_match', _('first match of a substring')),
       ('string_matches', _('all matches of a substring')),
       ('keywords_searcher', _('all matches of a list of keywords')),
       ('python_code', _('a script of a python function')),
       )


    name = models.CharField(max_length=60, help_text='name of the Labelling Function')
    label = models.CharField(max_length=60, help_text='Label Attributed for the Labelling Function')
    type = models.CharField(choices= templates, max_length=60, default='single_regex')
    content = models.TextField(default='', null=True, help_text='Searched Word or RegEx expression to match - '
                                                                            'in Text corresponding to selected label')
    project = models.ForeignKey(Project, related_name='project', on_delete=models.CASCADE, null=True,
                                help_text='Project ID where the Labelling Function is created')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function was created')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a labelling function was updated')

    def __str__(self):
        return self.name

    def has_permission(self, user):
        return self.project.has_permission(user)


class datadoc(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, unique=True, help_text='Task ID')
    text = models.TextField(default=None, null=True, help_text='Corresponding text')
    spacy_doc = models.JSONField('doc', default=None , help_text='SpaCy doc file relative to each Task in JSON Format')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a spacy model was run')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a spacy annotation was updated (added spans)')

    def has_permission(self, user):
        return self.project.has_permission(user)

    @classmethod

    def get_project_docs(self, project):
        docs = list(datadoc.objects.filter(project=project).values_list('spacy_doc', flat=True))
        nlp = spacy.load('en_core_web_sm')
        for idx, doc in enumerate(docs):
            docs[idx] = Doc(nlp.vocab).from_json(doc)
        return docs


class result(models.Model):
    function = models.ForeignKey(labelling_function, on_delete=models.CASCADE, help_text='labelling function ID')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, help_text='Task ID')

    result = models.TextField(null=True)
    label = models.CharField(max_length=60, null=True, help_text='label of the entity')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function is applied')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a function annotation was updated')

    model_version = models.TextField('labeling_function', null=True)

    def has_permission(self, user):
        return self.project.has_permission(user)


class aggregation_model(models.Model):
    templates = (
       ('HMM', _('hidden markov model')),
       ('Majority Voting', _('Majroity Voting')),
       )
    model_name = models.CharField(max_length=60, help_text='name of the Aggregation model')
    model_type = models.CharField(choices= templates, max_length=60)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    labels = models.JSONField('list of labels', default=None)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function is applied')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a function annotation was updated')
    
    disabled_functions = models.ManyToManyField(
        'labelling_function',
        related_name='LFs',
        help_text='selected labelling functions to ignore for the agg. model',
    )

    def has_permission(self, user):
        return self.project.has_permission(user)

    def get_labels(self):
        return list(self.labels)
    
    def get_initial_weights(self):
        fcts = self.disabled_functions.all()
        names = list(fcts.values_list('name', flat=True))
        weights = {fct:0 for fct in names}
        return weights



class aggregate_result(models.Model):

    model_version = models.ForeignKey(aggregation_model, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, help_text='Task ID')
    result = models.TextField(null=True, help_text='annotation results')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function is applied')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a function annotation was updated')
    
    def has_permission(self, user):
        return self.project.has_permission(user)


class metric(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    function = models.ForeignKey(labelling_function, on_delete=models.CASCADE, help_text='labelling function ID', null=True)
    model = models.ForeignKey(aggregation_model, on_delete=models.CASCADE, help_text='model ID', null=True)

    label = models.CharField(max_length=60, null=True, help_text='label of the entity')
    coverage = models.FloatField(null=True)
    conflicts = models.FloatField(null=True)
    overlaps = models.FloatField(null=True)
    
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    f1_score = models.FloatField(null=True)

    results = models.IntegerField(null=True)

    def has_permission(self, user):
        return self.project.has_permission(user)

