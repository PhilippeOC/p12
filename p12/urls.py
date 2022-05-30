from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from users.views import ClientCrud, EmployeeCrud
from events.views import (ClientEmployee,
                          ContractCru,
                          ContractEmployee,
                          EventRu,
                          EventEmployee,
                          Profil)


router = DefaultRouter()
router.register('employees', EmployeeCrud, basename="employees")
router.register('clients', ClientCrud,  basename="clients")
router.register('contracts', ContractCru, basename="contracts")
router.register('events', EventRu, basename="events")

router_contracts = DefaultRouter()
router_contracts.register('assignees', ContractEmployee, basename='contract_employee')

router_clients = DefaultRouter()
router_clients.register('assignees', ClientEmployee, basename='client_employee')

router_events = DefaultRouter()
router_events.register('assignees', EventEmployee, basename='event_employee')

router_profil = DefaultRouter()
router_profil.register('', Profil, basename='profil')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('contracts/<int:pk_contract>/', include(router_contracts.urls)),
    path('clients/<int:pk_client>/', include(router_clients.urls)),
    path('events/<int:pk_event>/', include(router_events.urls)),
    path('profil/', include(router_profil.urls))
]
