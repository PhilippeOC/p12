from rest_framework import viewsets

from users.serializers import EmployeeSerializer, ClientSerializer
from users.models import Employee, Client


class EmployeeCrud(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class ClientCrud(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
