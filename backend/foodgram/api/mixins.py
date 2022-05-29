from rest_framework import mixins, viewsets


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    pass


class CreateDeleteViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):
    pass
