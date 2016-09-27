from rest_framework import filters


def field_to_kwarg(field):
    return field.replace('.', '__')


class ParentLookupMapFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        lookup_map = view.parent_lookup_map

        kwargs = {
            field_to_kwarg(value): view.kwargs[key]
            for key, value in lookup_map.items()
        }
        return queryset.filter(**kwargs)


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_authenticated():
            return queryset.for_owner(request.user)
        else:
            return []
