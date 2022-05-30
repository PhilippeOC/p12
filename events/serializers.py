from rest_framework import serializers
from events.models import Event, Contract, ClientAssociation, ContractAssociation, EventAssociation
from users.serializers import ReadClientSerializer


class ContractSerializer(serializers.ModelSerializer):
    client = ReadClientSerializer(read_only=True)

    class Meta:
        model = Contract
        exclude = ['date_end']


class EventSerializer(serializers.ModelSerializer):
    client = ReadClientSerializer(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class ClientAssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientAssociation
        fields = ['id', 'employee_id', 'client_id', 'date_created']


class ContractAssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContractAssociation
        fields = ['id', 'employee_id', 'contract_id', 'date_created']


class EventAssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventAssociation
        fields = ['id', 'employee_id', 'event_id', 'date_created']


class ReadContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = ['id', 'amount']


class ReadEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'event_place']
