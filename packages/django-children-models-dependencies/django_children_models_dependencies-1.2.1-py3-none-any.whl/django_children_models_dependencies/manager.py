"""Provides the ``DependenciesManager`` class."""

from django.apps import apps
from django.db.models.fields import Field

from .utils import compute_dependencies_order


class ChildrenDependenciesManager:
    """Class to manage dependencies in models based on a parent one.

    This is historically used by ``Syncable`` but was extracted to also be used by
    ``Duplicable``.

    The main entry point is ``ChildrenDependenciesManager.get_children_dependencies`` which take a
    parent model, and will return all the models inheriting from this one in an order depending on
    dependencies: each dependencies of a model should come before this model in the list.

    The first time this method is called for a model, the result is cached, then the cache will
    be reused for the next calls.

    """

    @staticmethod
    def get_children_dependencies_specs(base_model):
        """Return all models inheriting from ``base_model`` with their dependencies.

        Returns
        -------
        list of tuplesl
            Each tuple as the representation of a model in the first entry, and a list of the
            representation of all dependeicies in the second entry.
            A representation of a model is a string following this format:
            %(app_label)s.%(model_name)s

        """
        # Will hold the data to return.
        specs = []

        def get_repr(model):
            """Return a representation of the given model."""
            return f"{model._meta.app_label}.{model._meta.model_name}"

        # Get all the models (excluding ones with a non-abstract parent model because
        # they are synced by their parent).
        models = [m for m in apps.get_models() if issubclass(m, base_model) and not m._meta.get_parent_list()]

        # Get all fields from the base model to avoid using them in dependencies.
        owned_fields = [f.name for f in base_model._meta.get_fields()]

        # Loop on each model to compute their dependencies.
        for model in models:
            # Get all fields related to other models, except ones defined in parents models.
            dependencies_fields = [
                f
                for f in model._meta.get_fields()
                if (
                    isinstance(f, Field)
                    and f.is_relation
                    and f.name not in owned_fields
                    and issubclass(f.related_model, base_model)
                    and f.related_model != model  # Ignore relations to self.
                )
            ]

            # If the model has no dependencies, we can stop here by adding an entry with
            # the model and an empty list of dependencies.
            if not dependencies_fields:
                specs.append((get_repr(model), []))
                continue

            # Get all parents for fields that inherits from non-abstract models.
            # And prepare also the reverse dict.
            non_abstract_parents = {}
            for field in dependencies_fields:
                parents = field.related_model._meta.get_parent_list()
                if parents:
                    non_abstract_parents[field.related_model] = parents[-1]  # Oldest ancestor.

            # Add an entry in the final result with the model and a list containing each
            # dependencies (or the parent non-abstract model if any)
            specs.append(
                (
                    get_repr(model),
                    [get_repr(non_abstract_parents.get(f.related_model, f.related_model)) for f in dependencies_fields],
                )
            )

        return specs

    @staticmethod
    def get_children_dependencies(base_model):
        """Return the ordered list of models.

        The ordering depends of the dependencies: each dependencies of a model should come
        before a model in the list.

        Returns
        -------
        list
            List the representation of all models inheriting from ``base_model``.

        """
        attr_name = f"{base_model._meta.app_label}__{base_model._meta.model_name}"

        if not getattr(ChildrenDependenciesManager, attr_name, None):
            # If the models list has not been populated yet, do it.

            # We compute the dependencies order.
            ordered_model_specs = compute_dependencies_order(
                ChildrenDependenciesManager.get_children_dependencies_specs(base_model)
            )

            # Then populate the list.
            setattr(ChildrenDependenciesManager, attr_name, [apps.get_model(m) for m in ordered_model_specs])

        # Return the previously or just populated list of models.
        return getattr(ChildrenDependenciesManager, attr_name)
