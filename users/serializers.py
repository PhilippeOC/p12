from rest_framework import serializers

from users.models import Employee, Client


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        user = super(). create(validated_data)
        user.set_password(validated_data.get('password'))
        user.is_active = True
        user.is_staff = True
        if user.role == 'M':
            user.is_superuser = True
        user.save()
        return user


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class ReadClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id', 'company_name']
