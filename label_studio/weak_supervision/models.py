from tracemalloc import start
from django.db import models
from projects.models import Project
from tasks.models import Task
from django.utils.translation import gettext_lazy as _

# Create your models here.

class labelling_function(models.Model):
    """
    Labelling Function class used for automatic data labeling in weak supervision
    
    """
    templates = (
       ('single_regex', _('first match of a regex pattern')),
       ('regex_matches', _('all matches of a regex pattern')),
       ('string_match', _('first match of a substring')),
       ('string_matches', _('all matches of a substring')),
       ('keywords_searcher', _('all matches of a list of keywords')),
       )
    name = models.CharField(max_length=60, help_text='name of the Labelling Function')
    label = models.CharField(max_length=60, help_text='Label Attributed for the Labelling Function')
    type = models.CharField(choices= templates, max_length=60, default='single_regex')
    content = models.TextField(default='Insert content here', null=True, help_text='Searched Word or RegEx expression to match - '
                                                                            'in Text corresponding to selected label')
    project = models.ForeignKey(Project, related_name='project', on_delete=models.CASCADE, null=True,
                                help_text='Project ID where the Labelling Function is created')


    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function was created')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a labelling function was updated')

    def __str__(self):
        return self.name

    def has_permission(self, user):
        return self.project.has_permission(user)

class weak_annotation_log(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, help_text='Task ID')
    text = models.TextField(default=None, null=True, help_text='Corresponding text')
    spacy_doc = models.JSONField('doc', default=None , help_text='SpaCy doc file relative to each Task in JSON Format')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a spacy model was run')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a spacy annotation was updated (added spans)')

    def has_permission(self, user):
        return self.project.has_permission(user)
    

class result(models.Model):
    function = models.ForeignKey(labelling_function, on_delete=models.CASCADE, help_text='labelling function ID')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, help_text='Task ID')

    start = models.IntegerField(_('start position'), null=True, help_text='start position of entity')
    end = models.IntegerField(_('end_position'), null=True, help_text='end position of entitiy')
    text = models.TextField(null=True, help_text='text of the entity')
    label = models.CharField(max_length=60, null=True, help_text='label of the entity')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function is applied')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a function annotation was updated')

    result = models.TextField('result', null=True)
    model_version = models.TextField('labeling_function', null=True)
    def has_permission(self, user):
        return self.project.has_permission(user)



class aggregate_result(models.Model):
    templates = (
       ('HMM', _('hidden markov model')),
       ('Majority Voting', _('Majroity Voting')),
       )
    model_name = models.CharField(max_length=60, help_text='name of the Aggregation model')
    model_type = models.CharField(choices= templates, max_length=60)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, help_text='Project ID')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, help_text='Task ID')
    annotation = models.TextField(null=True, help_text='text of the entity')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, help_text='Time a labelling function is applied')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, help_text='Last time a function annotation was updated')
    
    def has_permission(self, user):
        return self.project.has_permission(user)


class metric(models.Model):

    def has_permission(self, user):
        return self.project.has_permission(user)

