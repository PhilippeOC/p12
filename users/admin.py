from django.contrib import admin

from users.models import Employee, Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    list_display = ("id", "email", "first_name", "last_name", "company_name", "is_client")
    list_filter = ("company_name", "last_name", "is_client")
    search_fields = ['email', 'last_name']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    exclude = ('user_permissions', 'groups')
    list_display = ("id", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "last_name", "is_staff")
    search_fields = ['email', 'role' 'last_name']

    def has_delete_permission(self, request, obj=None):
        return False
