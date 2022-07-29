# Label Studio

## Introduction
Installing and running label studio locally or via the te cloud can be done following the steps here:

This folder holds all the pieces of the new weak supervision backend implementation framework.
**This branch ***dev/weak_supervision*** includes all the modifications concerning the added weak supervision part for NER to Label Studio.**

The weak supervision pipeline contains 3 steps:
- Creation of labelling functions
- Aggregating results from labelling functions using an aggregation model
- Applying a sequence model on top of the final results to generalize beyond the labelling functions

## Try out Label Studio
Installing and running label studio locally or via the te cloud can be done following the steps here:


## Module architecture 
### Files structure and properties

* `models.py`
    Includes the following models definition: labelling_functions, labelling_function_annotations, aggregation_models, aggregation_model_annotations, metrics, spacy_docs
* `serializers.py`
    Working with the Django Rest Framework (DRF), we use serializers to convert Django’s ORM querysets or objects to JSON format and vice-versa. 

* `api.py`
    Using the Django MTV pattern, the api.py file includes the view part (data formatting) in which we create the API calls using the DRF Viewsets. 
        - labelling_function CRUD
        - Executing LF
        - aggregation_model CRUD
        - Executing AGG_Model
        - Calculating metrics

    In DRF, working with serializers and viewsets go hand-in-hand. For example, create action will pass all the data to a serializer, and the serializer will create the object, return it in JSON format and the viewset will return it in HTTP response. Similarly in a retrieve action, the viewset will get the pk of the instance, get an instance from that pk and pass it to the serializer. Serializer will then serialize that object in JSON format and viewset will return in HTTP response.

* `urls.py`
    In order to register viewsets in urls, we have to use DRF Routers. In the application’s urls.py we create the router as well as the routes for the viewsets. 