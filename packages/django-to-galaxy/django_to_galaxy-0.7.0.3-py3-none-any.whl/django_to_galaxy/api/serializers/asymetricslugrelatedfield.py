from collections import OrderedDict

from rest_framework.relations import SlugRelatedField


class AsymetricSlugRelatedField(SlugRelatedField):
    def to_representation(self, value):
        return self.serializer_class(value).data

    # Get choices used by DRF autodoc and expect to_representation() to return an ID
    # We overload to use item.pk instead of to_representation()
    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([(item.pk, self.display_value(item)) for item in queryset])

    # DRF skip validations  when it only has id, we deactivate that
    def use_pk_only_optimization(self):
        return False

    @classmethod
    def from_serializer(cls, serializer, name=None, *args, **kwargs):
        if name is None:
            name = f"{serializer.__class__.__name__}AsymetricSlugAutoField"

        return type(name, (cls,), {"serializer_class": serializer})(*args, **kwargs)
