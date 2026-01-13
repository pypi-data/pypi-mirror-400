"""Exceptions for the ``django_children_models_dependencies`` app."""


class CircularRelationshipException(RuntimeError):
    """Raised when there is at least one circular dependency in the models."""

    pass


class UnresolvableDependenciesTree(Exception):
    """Raised when an undefined error happened when trying to resolve the dependencies tree."""

    pass
