from django.http.multipartparser import MultiPartParser
from rest_framework.mixins import *
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet


class CreateCustomMixin(CreateModelMixin):
    # parser_classes = (MultiPartParser, FormParser, JSONParser)

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = super(CreateCustomMixin, self).create(request, *args, **kwargs)
        return Response(serializer.data)



class CustomListModelMixin:
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        params = dict(request.GET)
        new_params = {}
        for each in params:
            if len(params[each]) == 1:
                new_params[each] = params[each][0]
            else:
                new_params[each + "__in"] = params[each]
        new_params.pop("page", None)

        queryset = self.model.objects.filter(**new_params).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListCustomMixin(CustomListModelMixin):
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):

        serializer = super(ListCustomMixin, self).list(request, *args, **kwargs)
        return Response(serializer.data)


class RetrieveCustomMixin(RetrieveModelMixin):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        serializer = super(RetrieveCustomMixin, self).retrieve(request, *args, **kwargs)
        return Response(serializer.data)


class UpdateCustomMixin(UpdateModelMixin):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        serializer = super(UpdateCustomMixin, self).update(request, *args, **kwargs)
        return Response(serializer.data)


class CustomModelViewSet(CreateCustomMixin,
                         RetrieveCustomMixin,
                         UpdateCustomMixin,
                         DestroyModelMixin,
                         ListCustomMixin,
                         GenericViewSet):
    """ Adaptation of DRF CustomViewSet """
    pass
