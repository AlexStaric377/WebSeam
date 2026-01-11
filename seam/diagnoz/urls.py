from django.urls import include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import backmeny
from . import views

# from diagnoz import views


urlpatterns = [
    # Предполагаем, что модальное окно находится на главной странице
    path('', views.home_view, name='home'),

    path('backpage', backmeny.backpage, name='backpage'),
    path('index', views.index, name='index'),
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
    path('likarinterwiev', views.likarinterwiev, name='likarinterwiev'),
    path('likarlistinterwiev', views.likarlistinterwiev, name='likarlistinterwiev'),
    path('likarreceptionpacient', views.likarreceptionpacient, name='likarreceptionpacient'),
    path('likarvisitngdays', views.likarvisitngdays, name='likarvisitngdays'),
    path('likarworkdiagnoz', views.likarworkdiagnoz, name='likarworkdiagnoz'),
    path('likarlibdiagnoz', views.likarlibdiagnoz, name='likarlibdiagnoz'),
    path('adminlanguage', views.adminlanguage, name='adminlanguage'),
    path('contentinterwiev', views.contentinterwiev, name='contentinterwiev'),
    path('featurespisok/<str:featurespisok_keyComplaint>,  <str:featurespisok_keyFeature>', views.featurespisok,
         name='featurespisok'),
    path('backfeature', views.backfeature, name='backfeature'),
    path('nextfeature/<str:nextfeature_keyComplaint>,  <str:nextfeature_name>', views.nextfeature, name='nextfeature'),

    path('nextgrdetaling', views.nextgrdetaling, name='nextgrdetaling'),
    path('enddetaling', views.enddetaling, name='enddetaling'),
    path('selectdetaling/<str:select_kodDetailing>', views.selectdetaling,
         name='selectdetaling'),
    path('selectgrdetaling/<str:select_kodDetailing>', views.selectgrdetaling, name='selectgrdetaling'),
    path('selectdiagnoz/<str:select_kodProtokola>, <str:select_nametInterview>', views.selectdiagnoz,
         name='selectdiagnoz'),
    path('receptfamilylikar', views.receptfamilylikar, name='receptfamilylikar'),
    path('receptprofillikar', views.receptprofillikar, name='receptprofillikar'),
    path('savediagnoz', views.savediagnoz, name='savediagnoz'),
    path('backdiagnoz', views.backdiagnoz, name='backdiagnoz'),
    path('receptprofillmedzaklad', views.receptprofillmedzaklad, name='receptprofillmedzaklad'),
    path('selectdprofillikar/<str:selected_kodzaklad>,  <str:selected_idstatus>,  <str:selected_name>',
         views.selectdprofillikar, name='selectdprofillikar'),
    path('backlistlikar', views.backlistlikar, name='backlistlikar'),
    path('backshablonselect', views.backshablonselect, name='backshablonselect'),
    path('inputprofilpacient/<str:selected_doctor>', views.inputprofilpacient, name='inputprofilpacient'),
    path('saveraceptionlikar', views.saveraceptionlikar, name='saveraceptionlikar'),
    path('accountuser', views.accountuser, name='accountuser'),
    path('rada', views.rada, name='rada'),
    path('newsseam', views.newsseam, name='newsseam'),
    path('kabinetpacient', views.kabinetpacient, name='kabinetpacient'),
    path('profilinterview/<str:selected_protokol>,  <str:selected_datevizita>, <str:selected_dateInterview>',
         views.profilinterview, name='profilinterview'),
    path('backprofilinterview', views.backprofilinterview, name='backprofilinterview'),
    path('profilpacient', views.profilpacient, name='profilpacient'),
    path('reestraccountuser', views.reestraccountuser, name='reestraccountuser'),
    path('exitkabinet', views.exitkabinet, name='exitkabinet'),
    path('backfromcontent', views.backfromcontent, name='backfromcontent'),
    path('selectvisitingdays/<str:selected_timevizita>,  <str:selected_datevizita>, <str:selected_daysoftheweek>',
         views.selectvisitingdays, name='selectvisitingdays'),
    path('proseam', views.proseam, name='proseam'),
    path('pronas', views.pronas, name='pronas'),
    path('zgoda', views.zgoda, name='zgoda'),
    path('workdiagnozlikar/<str:select_kodDoctor>,  <str:select_icd>, <int:select_id>', views.workdiagnozlikar,
         name='workdiagnozlikar'),
    path('libdiagnoz/<str:select_icdGrDiagnoz>', views.libdiagnoz, name='libdiagnoz'),
    path('contentinterview/<str:select_kodProtokola>', views.contentinterview, name='contentinterview'),
    path('directiondiagnoz', views.directiondiagnoz, name='directiondiagnoz'),
    path('likarnapryamok', views.likarnapryamok, name='likarnapryamok'),
    path('profillikarform', views.profillikarform, name='profillikarform'),
    path('removeinterview', views.removeinterview, name='removeinterview'),
    path('addworkdiagnoz', views.addworkdiagnoz, name='addworkdiagnoz'),
    path('deleteworkdiagnoz', views.deleteworkdiagnoz, name='deleteworkdiagnoz'),
    path('addgrupdiagnoz/<str:select_icdGrDiagnoz>', views.addgrupdiagnoz, name='addgrupdiagnoz'),
    path('deletprofil', views.deletprofil, name='deletprofil'),
    path('addvisitingdays', views.addvisitingdays, name='addvisitingdays'),
    path('profillmedzaklad/<str:select_icd>', views.profillmedzaklad, name='profillmedzaklad'),
    path('backlikarworkdiagnoz', views.backlikarworkdiagnoz, name='backlikarworkdiagnoz'),
    path('checkvisitinglikar', views.checkvisitinglikar, name='checkvisitinglikar'),
    path('addreceptpacientlikar', views.addreceptpacientlikar, name='addreceptpacientlikar'),
    path('pulstisktemp', views.pulstisktemp, name='pulstisktemp'),
    path('mapanalizkrovi', views.mapanalizkrovi, name='mapanalizkrovi'),
    path('mapanalizurines', views.mapanalizurines, name='mapanalizurines'),
    path('addanalizkrovi', views.addanalizkrovi, name='addanalizkrovi'),
    path('stanhealth', views.stanhealth, name='stanhealth'),
    path('recomentaktikhealing', views.recomentaktikhealing, name='recomentaktikhealing'),
    path('backworkdiagnozlikar', views.backworkdiagnozlikar, name='backworkdiagnozlikar'),

]
#
urlpatterns += [
    path("api-auth/", include('rest_framework.urls', namespace="rest_framework")),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# http GET http://192.168.1.113:50001/api/ApiControllerComplaint/ Accept:application/json
