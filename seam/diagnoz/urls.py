from django.urls import include
from django.urls import include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from diagnoz import views

urls_api = r'http GET http://192.168.1.113:50001/api/ApiControllerComplaint/ Accept:application/json'
urls_api_pk = r'http GET http://192.168.1.113:50001/api/ApiControllerComplaint/A.007/0/ Accept:application/json'

urlpatterns = [

    path('', views.index, name='home'),
    path('reception', views.reception, name='reception'),
    path('pacient', views.pacient, name='pacient'),
    path('likar', views.likar, name='likar'),
    path('setings', views.setings, name='setings'),
    path('receptinterwiev', views.InterwievListview.as_view(), name='receptinterwiev'),
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
    path('contentinterwiev', views.contentinterwiev, name='contentinterwiev'),
    #    path('nextfeature', views.nextfeature,  name='nextfeature'),
    path('featurespisok/<str:featurespisok_keyComplaint> <str:featurespisok_keyFeature> ', views.featurespisok,
         name='featurespisok'),
    path('nextfeature/<str:nextfeature_keyComplaint> <str:nextfeature_name>', views.nextfeature, name='nextfeature'),

]

urlpatterns += [
    path("api-auth/", include('rest_framework.urls', namespace="rest_framework")),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# http GET http://192.168.1.113:50001/api/ApiControllerComplaint/
# http GET http://192.168.1.113:50001/api/ApiControllerComplaint/ Accept:application/json
