
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404

from datetime import date
from collections import namedtuple
from typing import NamedTuple

from events.models import (ClientAssociation,
                           Contract,
                           ContractAssociation,
                           Event,
                           EventAssociation)

from users.models import Client, Employee
from users.permissions import BusinessPermissions, SupportPermissions, ManagerPermissions

from users.serializers import ReadClientSerializer


from events.serializers import (ClientAssociationSerializer,
                                ContractAssociationSerializer,
                                ContractSerializer,
                                EventAssociationSerializer,
                                EventSerializer,
                                ReadContractSerializer,
                                ReadEventSerializer)


class ContractDateFilter(filters.FilterSet):
    date_created = filters.IsoDateTimeFilter(field_name="date_created", lookup_expr='gte')
    date_created = filters.IsoDateTimeFilter(field_name="date_created", lookup_expr='lte')

    class Meta:
        model = Contract
        fields = '__all__'


class EventDateFilter(filters.FilterSet):
    date_created = filters.IsoDateTimeFilter(field_name="date_created", lookup_expr='gte')
    date_created = filters.IsoDateTimeFilter(field_name="date_created", lookup_expr='lte')

    class Meta:
        model = Event
        fields = '__all__'


class ContractCru(viewsets.ModelViewSet):
    """ Il n'est pas possible de supprimer un contrat """
    http_method_names = ['get', 'post', 'patch', 'put']
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [BusinessPermissions]
    filterset_fields = ['amount', 'signature_date']
    filterset_class = ContractDateFilter
    search_fields = ['amount', 'client__company_name']

    def retrieve(self, request, *args, **kwargs):
        """ lecture du détail d'un contrat """
        contract = Contract.objects.filter(id=self.kwargs['pk'])
        if not contract:
            raise ValidationError({"message": f"Le contrat {self.kwargs['pk']} n'existe pas."})
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """ creation d'un contrat avec un client existant """
        pk_client = request.data.get('client')
        client = get_object_or_404(Client, pk=pk_client)
        if client.is_client:
            contract = Contract.objects.filter(amount=request.data.get('amount'), client_id=pk_client)
            if contract.first():
                raise ValidationError({"message": "Ce contrat existe déjà."})
            Contract.objects.create(amount=request.data.get('amount'), client_id=pk_client)
            return Response({"message": "Le contrat est créé"},
                            status=status.HTTP_201_CREATED)
        return Response({"message": f"Le client {pk_client} est uniquement un prospect"},
                        status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """ signature d'un contrat et création de l'évènement """
        contract_object = self.get_object()
        if not contract_object.signature_date:
            contract_object.signature_date = date.today()
            Event.objects.create(event_place=request.data.get('event_place'),
                                 client_id=contract_object.client_id,
                                 notes=request.data.get('notes'))
            contract_object.save()
            return Response({"message": f"Le contrat {contract_object.id} est signé."},
                            status=status.HTTP_200_OK)
        return Response({"message": f"Le contrat {contract_object.id} est déjà signé!"},
                        status=status.HTTP_200_OK)


class EventRu(viewsets.ModelViewSet):
    """ Il n'est pas possible de créer un évènement (création automatique lors de la signature du contrat)
    Il n'est pas possible de supprimer un évènement"""
    http_method_names = ['get', 'patch', 'put']
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [SupportPermissions]
    filterset_fields = ['event_place', 'date_created', 'date_end']
    filterset_class = EventDateFilter
    search_fields = ['event_place', 'client__company_name']

    def retrieve(self, request, *args, **kwargs):
        event = Event.objects.filter(id=self.kwargs['pk'])
        if not event:
            raise ValidationError({"message": f"L'évènement {self.kwargs['pk']} n'existe pas."})
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """ date de fin d'un évènement """
        event = self.get_object()
        if not event.date_end:
            event.date_end = date.today()
            event.save()
            return Response({"message": f"L'évènement {event.id} est terminé."},
                            status=status.HTTP_200_OK)

        return Response({"message": f"L'évènement {event.id} est terminé depuis le {event.date_end}"},
                        status=status.HTTP_200_OK)


class ContractEmployee(viewsets.ModelViewSet):
    """ association entre un employé et un contrat """
    serializer_class = ContractAssociationSerializer
    permission_classes = [ManagerPermissions]

    def get_queryset(self):
        contract_association = ContractAssociation.objects.filter(contract_id=self.kwargs['pk_contract'])
        if not contract_association:
            if Contract.objects.filter(pk=self.kwargs['pk_contract']):
                raise ValidationError({'message':
                                       f"Le contrat {self.kwargs['pk_contract']} n'est pas associé à un employé."})
            else:
                raise ValidationError({'message': f"Le contrat {self.kwargs['pk_contract']} n'existe pas."})
        return contract_association

    def create(self, request, *args, **kwargs):
        contract_id = self.kwargs.get('pk_contract')
        if not Contract.objects.filter(pk=contract_id):
            raise ValidationError({'message': f"Le contrat {contract_id} n'existe pas."})

        employee = check_if_employee_exist(request)
        employee_id = employee.id
        employee_role = employee.role
        if employee_role != 'B':
            raise ValidationError({'message': f"L'employé {employee_id} n'appartient pas à l'équipe 'Business'."})

        if not ContractAssociation.objects.filter(contract_id=contract_id, employee_id=employee_id):
            if ContractAssociation.objects.filter(contract_id=contract_id, employee__role__contains='B'):
                return Response({"message": f"Le contrat {contract_id} est déjà attribué à un employé 'Business'"},
                                status=status.HTTP_200_OK)
            new_association = ContractAssociation.objects.create(contract_id=contract_id, employee_id=employee_id)
            serializer = ContractAssociationSerializer(new_association)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response({'message': f"Le contrat {contract_id} est déjà associé à l'employé {employee_id}."},
                        status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        if not ContractAssociation.objects.filter(contract_id=self.kwargs['pk_contract']):
            raise ValidationError({"message": f"Le contrat {self.kwargs['pk_contract']} n'existe pas."})
        association = new_association(ContractAssociation, request, self.kwargs['pk'])
        association.save()
        return super().partial_update(request, *args, **kwargs)


class EventEmployee(viewsets.ModelViewSet):
    """ association d'un employé à un évènement """
    serializer_class = EventAssociationSerializer
    permission_classes = [ManagerPermissions]

    def get_queryset(self):
        event_association = EventAssociation.objects.filter(event_id=self.kwargs['pk_event'])
        if not event_association:
            if Event.objects.filter(pk=self.kwargs['pk_event']):
                raise ValidationError({'message':
                                      f"L'evènement {self.kwargs['pk_event']} n'est pas associé à un employé."})
            else:
                raise ValidationError({'message': f"L'evènement {self.kwargs['pk_event']} n'existe pas"})
        return event_association

    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('pk_event')
        if not Event.objects.filter(pk=event_id):
            raise ValidationError({'message': f"L'évènement {event_id} n'existe pas."})

        employee = check_if_employee_exist(request)
        employee_id = employee.id
        employee_role = employee.role
        if employee_role != 'S':
            raise ValidationError({'message': f"L'employé {employee_id} n'appartient pas à l'équipe 'Support'."})

        if not EventAssociation.objects.filter(event_id=event_id, employee_id=employee_id):
            if EventAssociation.objects.filter(event_id=event_id, employee__role__contains='S'):
                return Response({"message": f"L'évènement {event_id} est déjà attribué à un employé 'Support'"},
                                status=status.HTTP_200_OK)
            new_association = EventAssociation.objects.create(event_id=event_id, employee_id=employee_id)
            serializer = EventAssociationSerializer(new_association)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response({'message': f"L'évènement {event_id} est déjà associé à l'employé {employee_id}."},
                        status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        if not EventAssociation.objects.filter(event_id=self.kwargs['pk_event']):
            raise ValidationError({"message": f"L'évènement {self.kwargs['pk_event']} n'existe pas."})
        association = new_association(EventAssociation, request, self.kwargs['pk'])
        association.save()
        return super().partial_update(request, *args, **kwargs)


class ClientEmployee(viewsets.ModelViewSet):
    """ association entre un employé et un client """
    serializer_class = ClientAssociationSerializer
    permission_classes = [ManagerPermissions]

    def get_queryset(self):
        client_association = ClientAssociation.objects.filter(client_id=self.kwargs['pk_client'])
        if not client_association:
            if Client.objects.filter(pk=self.kwargs['pk_client']):
                raise ValidationError({'message':
                                      f"Le client {self.kwargs['pk_client']} n'est pas associé à un employé."})
            else:
                raise ValidationError({'message': f"Le client {self.kwargs['pk_client']} n'existe pas."})
        return client_association

    def create(self, request, *args, **kwargs):
        client_id = self.kwargs.get('pk_client')
        client = Client.objects.filter(pk=client_id)
        if not client:
            raise ValidationError({'message': f"Le client {client_id} n'existe pas."})
        if client.first().company_name == '***':
            raise ValidationError({'message': f"Le client {client_id} est anonyme."})
        employee = check_if_employee_exist(request)
        employee_id = employee.id
        employee_role = employee.role

        role = {'B': 'Business', 'S': 'Support'}
        if not ClientAssociation.objects.filter(client_id=client_id, employee_id=employee_id):
            if ClientAssociation.objects.filter(client_id=client_id, employee__role__contains=employee_role):
                return Response({"message":
                                f"Le client {client_id} est déjà suivi par un employé '{role.get(employee_role)}'"},
                                status=status.HTTP_200_OK)

            if not client.first().is_client and employee.role == 'S':
                raise ValidationError({'message': f"Le client {client_id} est un prospect. "
                                       "Il ne peut être suivi par un employé 'support'."})
            new_association = ClientAssociation.objects.create(client_id=client_id, employee_id=employee_id)
            serializer = ClientAssociationSerializer(new_association)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response({'message': f"Le client {client_id} est déjà associé à l'employé {employee_id}."},
                        status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        if not ClientAssociation.objects.filter(id=self.kwargs['pk']):
            raise ValidationError({"message": f"L'association {self.kwargs['pk']} n'existe pas."})
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not ClientAssociation.objects.filter(client_id=self.kwargs['pk_client']):
            raise ValidationError({"message": f"Le client {self.kwargs['pk_client']} n'existe pas."})
        association = new_association(ClientAssociation, request, self.kwargs['pk'])
        association.save()
        return super().partial_update(request, *args, **kwargs)


class Profil(viewsets.ModelViewSet):
    http_method_names = ['get']

    def list(self, request):
        emp = Employee.objects.get(pk=self.request.user.id)
        my_clients = emp.customers.all()
        my_contracts = emp.contracts.all()
        my_events = emp.events.all()
        my_datas = {}
        if 'clients' in self.request.query_params:
            my_datas['clients'] = ReadClientSerializer(my_clients, many=True).data
        if 'contracts' in self.request.query_params:
            my_datas['contracts'] = ReadContractSerializer(my_contracts, many=True).data
        if 'events' in self.request.query_params:
            my_datas['events'] = ReadEventSerializer(my_events, many=True).data
        return Response({'clients': my_datas.get('clients'),
                         'contracts': my_datas.get('contracts'),
                         'events': my_datas.get('events')},
                        status=status.HTTP_200_OK)


def check_if_employee_exist(request) -> NamedTuple:
    """ retourne l'id et le role d'un employé s'il existe """
    employee = namedtuple('employee', ['id', 'role'])
    if not request.data.get('employee'):
        raise ValidationError({'message': "Le champ 'employee' (clé-valeur) est obligatoire."})
    employee_id = request.data.get('employee')
    employee_role = Employee.get_employee_role(employee_id)
    if not employee_role:
        raise ValidationError({'message': f"L'employé {employee_id} n'existe pas"})
    if Employee.is_anonymize(employee_id):
        raise ValidationError({'message': f"L'employé {employee_id} est anonyme"})
    return employee(employee_id, employee_role)


def new_association(obj_association, request, pk):
    """ création d'une nouvelle association lorsqu'un employé est rendu anonyme"""
    association = obj_association.objects.filter(id=pk).first()
    if not association:
        raise ValidationError({"message": f"L'association {pk} n'existe pas."})
    employee = check_if_employee_exist(request)
    employee_id = employee.id
    employee_role = employee.role
    role = Employee.get_employee_role(association.employee_id)
    if role != employee_role:
        raise ValidationError({"message": "Le nouvel employé doit avoir le même role que son prédécesseur."})
    association.employee_id = employee_id
    return association
