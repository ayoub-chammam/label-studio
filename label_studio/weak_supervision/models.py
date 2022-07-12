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
