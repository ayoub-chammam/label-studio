from rest_framework import filters

class ProjectSearchFilter(filters.SearchFilter):
    search_param = "Project"
    search_description = 'project ID'


class LabelSearchFilter(filters.SearchFilter):
    search_param = "Label"
    search_description = 'Entity Label'


class LFSearchFilter(filters.SearchFilter):
    search_param = "Labelling Function"
    search_description = 'Labelling Function ID'


class ModelSearchFilter(filters.SearchFilter):
    search_param = "Model ID"
    search_description = 'Aggregation model ID'

