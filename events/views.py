from rest_framework import viewsets

from events.models import (ClientAssociation,
                           Contract,
                           ContractAssociation,
                           Event,
                           EventAssociation)

from events.serializers import (ClientAssociationSerializer,
                                ContractAssociationSerializer,
                                ContractSerializer,
                                EventAssociationSerializer,
                                EventSerializer)


class ContractCrud(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


class EventRud(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ContractEmployee(viewsets.ModelViewSet):
    queryset = ContractAssociation.objects.all()
    serializer_class = ContractAssociationSerializer


class EventEmployee(viewsets.ModelViewSet):
    queryset = EventAssociation.objects.all()
    serializer_class = EventAssociationSerializer


class ClientEmployee(viewsets.ModelViewSet):
    queryset = ClientAssociation.objects.all()
    serializer_class = ClientAssociationSerializer
