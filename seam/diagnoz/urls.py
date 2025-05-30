from django.urls import include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from diagnoz import views

# urls_api = r'http GET http://192.168.1.113:50001/api/ApiControllerComplaint/ Accept:application/json'
# urls_api_pk = r'http GET http://192.168.1.113:50001/api/ApiControllerComplaint/A.007/0/ Accept:application/json'

urlpatterns = [

    path('', views.index, name='home'),
    path('reception', views.reception, name='reception'),
    path('pacient', views.pacient, name='pacient'),
    path('likar', views.likar, name='likar'),
    path('setings', views.setings, name='setings'),
    path('receptinterwiev', views.interwievcomplaint, name='receptinterwiev'),
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
    path(
        'featurespisok/<str:featurespisok_keyComplaint>,  <str:featurespisok_keyFeature>,  <str:featurespisok_nameFeature>',
        views.featurespisok,
         name='featurespisok'),
    path('nextfeature/<str:nextfeature_keyComplaint>,  <str:nextfeature_name>', views.nextfeature, name='nextfeature'),
    path('glavmeny', views.glavmeny, name='glavmeny'),
    path('nextgrdetaling', views.nextgrdetaling, name='nextgrdetaling'),
    path('enddetaling', views.enddetaling, name='enddetaling'),
    path('selectdetaling/<str:select_kodDetailing>, <str:select_nameDetailing>', views.selectdetaling,
         name='selectdetaling'),
    path('selectgrdetaling/<str:select_kodDetailing>,  <str:select_nameGrDetailing>', views.selectgrdetaling,
         name='selectgrdetaling'),
    path('selectdiagnoz/<str:select_kodProtokola>, <str:select_nametInterview>', views.selectdiagnoz,
         name='selectdiagnoz'),
    path('receptfamilylikar', views.receptfamilylikar, name='receptfamilylikar'),
    path('receptprofillikar', views.receptprofillikar, name='receptprofillikar'),
    path('savediagnoz', views.savediagnoz, name='savediagnoz'),
    path('backdiagnoz', views.backdiagnoz, name='backdiagnoz'),
    path('receptprofillmedzaklad', views.receptprofillmedzaklad, name='receptprofillmedzaklad'),
    path('selectdprofillikar/<str:selected_edrpou>  <str:selected_idstatus>  <str:selected_name>',
         views.selectdprofillikar,
         name='selectdprofillikar'),
    path('inputprofilpacient/<str:selected_doctor>', views.inputprofilpacient, name='inputprofilpacient'),
    path('saveraceptionlikar', views.saveraceptionlikar, name='saveraceptionlikar'),
    path('accountuser', views.accountuser, name='accountuser'),
    path('kabinetpacient', views.kabinetpacient, name='kabinetpacient'),
    path('profilinterview', views.profilinterview, name='profilinterview')
]

urlpatterns += [
    path("api-auth/", include('rest_framework.urls', namespace="rest_framework")),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# http GET http://192.168.1.113:50001/api/ApiControllerComplaint/ Accept:application/json
