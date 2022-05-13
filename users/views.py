from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from users.serializers import EmployeeSerializer, ClientSerializer
from users.models import Employee, Client
from users.permissions import PermissionsAccesClients, ManagerPermissions

from events.models import ClientAssociation, EventAssociation, ContractAssociation


class EmployeeCrud(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [ManagerPermissions]

    def destroy(self, request, *args, **kwargs):
        """ permet de rendre anonyme un employé """
        employee = Employee.objects.filter(pk=kwargs['pk']).first()
        if not employee:
            raise ValidationError({'message': f"L'employé {kwargs['pk']} n'existe pas."})
        event_link = EventAssociation.objects.filter(employee_id=kwargs['pk']).values_list('event_id', flat=True)
        contract_link = ContractAssociation.objects.filter(employee_id=kwargs['pk']).values_list('contract_id',
                                                                                                 flat=True)
        client_link = ClientAssociation.objects.filter(employee_id=kwargs['pk']).values_list('client_id', flat=True)

        Employee.anonymize(employee).save()
        return Response({"message": f"L'employé {kwargs['pk']} est rendu anonyme."
                         f" Il est lié aux évènements {list(event_link)},"
                         f" aux contrats {list(contract_link)},"
                         f" aux clients {list(client_link)}."},
                        status=status.HTTP_200_OK)


class ClientCrud(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [PermissionsAccesClients]

    def partial_update(self, request, *args, **kwargs):
        """ convertion d'un client potentiel en client existant """
        client_object = self.get_object()
        client_object.is_client = True
        client_object.save()
        return Response({"message": f"Le client {client_object.id} existe."},
                        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """ permet de rendre anonyme un client """
        client = Client.objects.filter(pk=kwargs['pk']).first()
        if not client:
            raise ValidationError({'message': f"Le client {kwargs['pk']} n'existe pas."})
        employee_link = ClientAssociation.objects.filter(client_id=kwargs['pk']).values_list('employee_id', flat=True)
        Client.anonymize(client).save()
        return Response({"message": f"Le client {kwargs['pk']} est rendu anonyme."
                         f" Il est lié aux employés {list(employee_link)}."},
                        status=status.HTTP_200_OK)
