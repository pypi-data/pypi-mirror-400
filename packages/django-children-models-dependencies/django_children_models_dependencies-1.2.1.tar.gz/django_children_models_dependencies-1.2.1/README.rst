===================================
Django Children Models Dependencies
===================================

Purpose
=======

This is a small app that allow to get the children of a base model, in an dependency order from
the model with the less dependencies, to the model with the more dependencies, each model coming
after its own dependencies

For example, for theses models:

.. code-block:: python

    class BaseModel(models.Model):
        class Meta:
            abstract = True

    class ChildModel1(BaseModel):
        pass

    class ChildModel2(BaseModel):
        link = models.ForeignKey('myapp.ChildModel3', on_delete=models.CASCADE)


    class ChildModel3(BaseModel):
        pass


The order will be:

.. code-block:: python

        from django_children_models_dependencies.manager import ChildrenDependenciesManager

        self.assertListEqual(ChildrenDependenciesManager.get_children_dependencies(BaseModel), [
            ChildModel1,  # first model without dependencies
            ChildModel3,  # dependency of ChildModel2, so it comes before
            ChildModel2,  # last one, which must come after its own dependencies
        ])


Installation
============

Install from PyPI:

.. code-block:: sh

    pip install django-children-models-dependencies


Requirements
============

- Python 3.9, 3.10, 3.11, 3.12
- Django 4.2, 5.0, 5.1
