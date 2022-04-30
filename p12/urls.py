from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import EmployeeCrud, ClientCrud


router = DefaultRouter()
router.register('employees', EmployeeCrud, basename="employees")
router.register('clients', ClientCrud,  basename="clients")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
