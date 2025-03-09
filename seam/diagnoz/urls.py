from django.contrib.auth.models import User
from django.urls import include
from django.urls import path
from rest_framework import routers, serializers, viewsets

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('api-auth/', include('rest_framework.urls')),
    path('reception', views.reception, name='reception'),
    path('pacient', views.pacient, name='pacient'),
    path('likar', views.likar, name='likar'),
    path('admin', views.admin, name='admin'),
    path('receptinterwiev', views.receptinterwiev, name='receptinterwiev'),
    path('pacientprofil', views.pacientprofil, name='pacientprofil'),
    path('pacientinterwiev', views.pacientinterwiev, name='pacientinterwiev'),
    path('pacientlistinterwiev', views.pacientlistinterwiev, name='pacientlistinterwiev'),
    path('pacientreceptionlikar', views.pacientreceptionlikar, name='pacientreceptionlikar'),
    path('pacientstanhealth', views.pacientstanhealth, name='pacientstanhealth'),
    path('likarprofil', views.likarprofil, name='likarprofil'),
    path('likarinterweiv', views.likarinterweiv, name='likarinterweiv'),
    path('likarlistinterweiv', views.likarlistinterweiv, name='likarlistinterweiv'),
    path('likarreceptionpacient', views.likarreceptionpacient, name='likarreceptionpacient'),
    path('likarvisitngdays', views.likarvisitngdays, name='likarvisitngdays'),
    path('likarworkdiagnoz', views.likarworkdiagnoz, name='likarworkdiagnoz'),
    path('likarlibdiagnoz', views.likarlibdiagnoz, name='likarlibdiagnoz'),
    path('adminlanguage', views.adminlanguage, name='adminlanguage'),
    path('contentinterwiev', views.contentinterwiev, name='contentinterwiev')

]


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns += [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
