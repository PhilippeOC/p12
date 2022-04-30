from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import ClientCrud, EmployeeCrud
from events.views import (ClientEmployee,
                          ContractCrud,
                          ContractEmployee,
                          EventRud,
                          EventEmployee)


router = DefaultRouter()
router.register('employees', EmployeeCrud, basename="employees")
router.register('clients', ClientCrud,  basename="clients")
router.register('contracts', ContractCrud, basename="contracts")
router.register('events', EventRud, basename="events")

router_contracts = DefaultRouter()
router_contracts.register('assignees', ContractEmployee, basename='contract_employee')

router_clients = DefaultRouter()
router_clients.register('assignees', ClientEmployee, basename='client_employee')

router_events = DefaultRouter()
router_events.register('assignees', EventEmployee, basename='event_employee')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('contracts/<int:pk_contract>/', include(router_contracts.urls)),
    path('clients/<int:pk_client>/', include(router_clients.urls)),
    path('events/<int:pk_event>/', include(router_events.urls)),
]
