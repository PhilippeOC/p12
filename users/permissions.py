from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from events.models import ClientAssociation, EventAssociation, ContractAssociation
from users.models import Employee


class ManagerPermissions(permissions.BasePermission):
    """ permissions accordées aux super utilisateurs (groupe manager) """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        raise ValidationError({"message": "Accès réservé aux managers."})


class SupportPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if not EventAssociation.objects.filter(employee_id=request.user.id, event_id=obj.id):
            raise ValidationError({"message": f"Vous n'êtes pas responsable de l'évènement {obj.id}."})
        return True


class PermissionsAccesClients(permissions.BasePermission):
    def has_permission(self, request, view):
        employeeId = request.user.id
        role = Employee.get_employee_role(employeeId)
        if request.method in ['POST', 'PATCH']:
            if role == 'S':
                raise ValidationError({"message": "Seuls les employés 'Business' ou 'Manager' "
                                       "peuvent ajouter ou modifier le status d'un client."})
        if request.method == 'DELETE':
            if not request.user.is_superuser:
                raise ValidationError({"message": "Accès réservé aux managers."})
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if not ClientAssociation.objects.filter(employee_id=request.user.id, client_id=obj.id):
            raise ValidationError({"message": f"Vous n'êtes pas responsable du client {obj.id}."})
        return True


class BusinessPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'POST':
            client_id = request.data.get('client')
            if request.user.role == 'S':
                raise ValidationError({"message": "Un employé 'Support' ne peut pas créer de contrat."})
            if not ClientAssociation.objects.filter(client_id=client_id, employee_id=request.user.id):
                raise ValidationError({"message": f"Vous n'êtes pas responsable du client {client_id}."})
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if not ContractAssociation.objects.filter(contract_id=obj.id, employee_id=request.user.id):
            raise ValidationError({"message": f"Vous n'êtes pas responsable du contrat {obj.id}."})
        return True
