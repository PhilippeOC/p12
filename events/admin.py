from django.contrib import admin

from events.models import Contract, Event, ClientAssociation, ContractAssociation, EventAssociation


@admin.display(description='amount')
def add_euro(obj):
    return str(obj.amount) + ' €'


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    exclude = ('date_end',)
    list_display = ('id', add_euro, 'signature_date', 'client_id')
    list_filter = ("amount", "signature_date", "client")
    search_fields = ['amount', 'signature_date']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'event_place', 'client_id')
    list_filter = ('date_created', 'client_id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContractAssociation)
class ContractAssociationAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract_id', 'employee_id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EventAssociation)
class EventAssociationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_id', 'employee_id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClientAssociation)
class ClientAssociationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_id', 'employee_id')

    def has_delete_permission(self, request, obj=None):
        return False
