import json

import environ
import pyodbc
import requests
from django.shortcuts import render

from diagnoz import settingsvar


def rest_api(api_url):
    env = environ.Env()
    urls_api = env('urls_api')
    urls = urls_api + api_url
    response = requests.get(urls)
    return json.loads(response.content)

def index(request):  # httpRequest
    return render(request, 'diagnoz/index.html')


def glavmeny(request):
    return render(request, 'diagnoz/glavmeny.html')

def reception(request):  # httpRequest
    return render(request, 'diagnoz/reception.html')


def pacient(request):  # httpRequest
    return render(request, 'diagnoz/pacient.html')


def likar(request):  # httpRequest
    return render(request, 'diagnoz/likar.html')


def setings(request):  # httpRequest
    return render(request, 'diagnoz/setings.html')


# --- Блок Опитування і встановлення діагнозу
# --- 1. Де або яке нездужання
# class InterwievListview(ListView):
#    model = Complaint
#    template_name = 'diagnoz/receptinterwiev.html'
#    context_object_name = 'complaintlist'

#    extra_context = {
#        'complaintlist': rest_api('api/ApiControllerComplaint/')
#    }

def cleanvars():
    settingsvar.feature_name = ""
    settingsvar.spisokkeyfeature = []
    settingsvar.spisoknamefeature = []
    settingsvar.listfeature = {}
    settingsvar.listgrdetaling = {}
    settingsvar.listdetaling = {}
    settingsvar.spisoklistdetaling = []
    settingsvar.spisokGrDetailing = []
    settingsvar.spisokselectDetailing = []
    settingsvar.spselectnameDetailing = []
    settingsvar.rest_apiGrDetaling = ""
    settingsvar.viewdetaling = False
    settingsvar.viewgrdetaling = False
    settingsvar.DiagnozRecomendaciya = []
    settingsvar.rest_apisetdiagnoz = ""
    settingsvar.html = ""
    settingsvar.nextstepdata = {}
    settingsvar.spisokkeyinterview = []
    settingsvar.spisoknameinterview = []
    settingsvar.strokagrdetaling = ""
    settingsvar.strokagrdetaling = ""
    settingsvar.diagnozStroka = []
    return


def interwievcomplaint(request):
    cleanvars()
    data = {
        'complaintlist': rest_api('api/ApiControllerComplaint/')
    }
    return render(request, 'diagnoz/receptinterwiev.html', context=data)


# --- 2. Характер нездужання

def nextfeature(request, nextfeature_keyComplaint, nextfeature_name):
    settingsvar.DiagnozRecomendaciya.append(nextfeature_keyComplaint + ";")
    settingsvar.strokagrdetaling = settingsvar.strokagrdetaling + nextfeature_keyComplaint + ";"
    settingsvar.spisokkeyinterview.append(nextfeature_keyComplaint + ";")
    settingsvar.feature_name = nextfeature_name
    settingsvar.listfeature = {}
    if len(settingsvar.listfeature) <= 0:
        settingsvar.listfeature = rest_api('api/FeatureController/' + "0/" + nextfeature_keyComplaint + "/0/")
    html = 'diagnoz/nextfeature.html'
    data = {
        'compl': nextfeature_name,
        'next': '  Далі ',
        'featurelist': settingsvar.listfeature
    }
    return render(request, html, context=data)


def featurespisok(request, featurespisok_keyComplaint, featurespisok_keyFeature, featurespisok_nameFeature):
    # --- добавить контлоь цепочек груп
    #    str = settingsvar.strokagrdetaling+featurespisok_keyFeature+";"
    #    CmdStroka = rest_api('/api/InterviewController/' + "0/0/0/0/" +  str)
    #    if  len(CmdStroka)>0:
    settingsvar.DiagnozRecomendaciya.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyinterview.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyfeature.append(featurespisok_keyFeature)
    settingsvar.spisoknamefeature.append(featurespisok_nameFeature)
    index = 0
    if len(settingsvar.listfeature) > 0:
        for item in settingsvar.listfeature:
            if featurespisok_keyFeature == item['keyFeature']:
                del settingsvar.listfeature[index]

                data = {
                    'compl': settingsvar.feature_name,
                    'next': '  Далі ',
                    'featurelist': settingsvar.listfeature
                }
                return render(request, 'diagnoz/nextfeature.html', context=data)
            index = index + 1
    return render(request, 'diagnoz/errorfeature.html')


# --- 3. Деталізація характеру нездужання

def nextgrdetaling(request):
    nextstepgrdetaling()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Блок поиска и вывода описания диагноза

# --- функция распределения списков симптомов по локальным и групповым
def nextstepgrdetaling():
    settingsvar.listdetaling = {}
    settingsvar.spisokselectDetailing = []
    settingsvar.spisokGrDetailing = []
    if len(settingsvar.spisokkeyfeature) > 0:
        for keyfeature in settingsvar.spisokkeyfeature:
            listkeyfeature = rest_api('api/DetailingController/' + "0/" + keyfeature + "/0/")
            for itemkeyfeature in listkeyfeature:
                set = ""
                if itemkeyfeature['keyGrDetailing'] != None:
                    if itemkeyfeature['keyFeature'] in settingsvar.strokagrdetaling:
                        if itemkeyfeature['keyGrDetailing'] not in settingsvar.strokagrdetaling:
                            set = settingsvar.strokagrdetaling + itemkeyfeature['keyGrDetailing'] + ";"
                    else:
                        set = settingsvar.strokagrdetaling + itemkeyfeature['keyFeature'] + ";" + itemkeyfeature[
                            'keyGrDetailing'] + ";"
                    if len(set) != 0:
                        CmdStroka = rest_api('/api/InterviewController/' + "0/0/0/0/" + set)
                        if len(CmdStroka) > 0:
                            settingsvar.strokagrdetaling = set
                            settingsvar.spisokGrDetailing.append(itemkeyfeature['keyGrDetailing'])
                else:
                    settingsvar.spisoklistdetaling.append(itemkeyfeature)
            if len(settingsvar.spisoklistdetaling) > 0:
                enddetaling = 'enddetaling'
                listdetaling = settingsvar.spisoklistdetaling
                settingsvar.nextstepdata = {
                    'nextdetali': enddetaling,
                    'compl': settingsvar.feature_name,
                    'next': '  Далі ',
                    'detalinglist': settingsvar.spisoklistdetaling
                }
                settingsvar.html = 'diagnoz/detaling.html'
                del settingsvar.spisokkeyfeature[0]
                return
            if len(settingsvar.spisokGrDetailing) > 0:
                for itemgrdetaling in settingsvar.spisokGrDetailing:
                    settingsvar.rest_apiGrDetaling = rest_api(
                        '/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/")
                    settingsvar.nextstepdata = {
                        'compl': settingsvar.feature_name,
                        'next': '  Далі ',
                        'detalinglist': settingsvar.rest_apiGrDetaling
                    }
                    settingsvar.html = 'diagnoz/grdetaling.html'
                    del settingsvar.spisokkeyfeature[0]
                    return
            else:
                del settingsvar.spisokkeyfeature[0]
            keyfeature = ""
        if len(keyfeature) == 0 and len(settingsvar.spisokkeyfeature) > 0: del settingsvar.spisokkeyfeature[0]
        return
    if len(settingsvar.DiagnozRecomendaciya) == 0:
        cleanvars()
        settingsvar.nextstepdata = {
            'complaintlist': rest_api('api/ApiControllerComplaint/')
        }
        settingsvar.html = 'diagnoz/receptinterwiev.html'

    return


# ---  вибір деталізації симптому нездужання
def selectdetaling(request, select_kodDetailing, select_nameDetailing):
    settingsvar.spisokkeyinterview.append(select_kodDetailing + ";")
    settingsvar.spisokselectDetailing.append(select_kodDetailing)
    settingsvar.spselectnameDetailing.append(select_nameDetailing)
    index = 0
    if len(settingsvar.spisoklistdetaling) > 0:
        settingsvar.viewdetaling = True
        for item in settingsvar.spisoklistdetaling:
            add = False
            lstDiagnoz = []
            for lst in settingsvar.DiagnozRecomendaciya:
                if item['keyFeature'] in lst:
                    add = True
                    lstDiagnoz.append(lst)
                else:
                    if add == True:
                        lstDiagnoz.append(item['kodDetailing'] + ";")
                        lstDiagnoz.append(lst)
                        add = False
                    else:
                        lstDiagnoz.append(lst)
            settingsvar.DiagnozRecomendaciya = lstDiagnoz
            if select_kodDetailing == item['kodDetailing']:
                del settingsvar.spisoklistdetaling[index]
            index = index + 1
            enddetaling = 'enddetaling'
            data = {
                'nextdetali': enddetaling,
                'compl': settingsvar.feature_name + ', Деталізація характеру',
                'next': '  Далі ',
                'detalinglist': settingsvar.spisoklistdetaling
            }
        return render(request, 'diagnoz/detaling.html', context=data)

    return render(request, 'diagnoz/grdetaling.html', context=data)


# ---  вибір деталізації симптому нездужання
def selectgrdetaling(request, select_kodDetailing, select_nameGrDetailing):
    settingsvar.DiagnozRecomendaciya.append(select_kodDetailing + ";")
    settingsvar.spisokkeyinterview.append(select_kodDetailing + ";")
    settingsvar.spisokselectDetailing.append(select_kodDetailing)
    settingsvar.spselectnameDetailing.append(select_nameGrDetailing)
    index = 0
    if len(settingsvar.rest_apiGrDetaling) > 0:
        for item in settingsvar.rest_apiGrDetaling:
            if select_kodDetailing == item['kodDetailing']:
                del settingsvar.rest_apiGrDetaling[index]
                data = {
                    'compl': settingsvar.feature_name + ', Деталізація характеру',
                    'next': '  Далі ',
                    'detalinglist': settingsvar.rest_apiGrDetaling
                }
                return render(request, 'diagnoz/grdetaling.html', context=data)
            index = index + 1
    return render(request, 'diagnoz/errorfeature.html')


# --- кінець інтервью, пошук та виведення  попереднього діагнозу
def enddetaling(request):
    if len(settingsvar.spisokkeyfeature) > 0:
        if (settingsvar.viewdetaling == False and len(settingsvar.spisoklistdetaling) > 0):
            listdetaling = settingsvar.spisoklistdetaling
            data = {
                'compl': settingsvar.feature_name + ', Деталізація характеру',
                'next': '  Далі ',
                'detalinglist': listdetaling
            }
            settingsvar.viewdetaling = True
            del settingsvar.spisokkeyfeature[0]
            return render(request, 'diagnoz/detaling.html', context=data)
        else:
            settingsvar.spisoklistdetaling = []

        if len(settingsvar.spisokGrDetailing) > 0:
            del settingsvar.spisokGrDetailing[0]
            for itemgrdetaling in settingsvar.spisokGrDetailing:
                settingsvar.rest_apiGrDetaling = rest_api('/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/")
                data = {
                    'compl': settingsvar.feature_name + ', Деталізація характеру',
                    'next': '  Далі ',
                    'detalinglist': settingsvar.rest_apiGrDetaling
                }
                #                    del settingsvar.spisokGrDetailing[itemgrdetaling]
                return render(request, 'diagnoz/grdetaling.html', context=data)

        if len(settingsvar.spisokkeyfeature) > 0:
            nextstepgrdetaling()
            if len(settingsvar.spisokkeyfeature) == 0 and len(settingsvar.spisoklistdetaling) == 0 and len(
                    settingsvar.spisokGrDetailing) == 0:
                diagnoz()
    else:
        diagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def writediagnoz(select_kodProtokola, select_nametInterview):
    settingsvar.kodProtokola = select_kodProtokola
    settingsvar.nametInterview = select_nametInterview
    for item in settingsvar.diagnozStroka:
        if select_kodProtokola == item['kodProtokola']:
            api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0")
            apiicd = rest_api('/api/DiagnozController/' + api['kodDiagnoz'] + "/0/0")
            settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
            api = rest_api('/api/RecommendationController/' + api['kodRecommend'] + "/0")
            settingsvar.html = 'diagnoz/versiyadiagnoza.html'
            settingsvar.nextstepdata = {
                'opis': item['opistInterview'],
                'http': item['uriInterview'],
                'rekomendaciya': api['contentRecommendation'],
                'compl': select_nametInterview,
                'detalinglist': settingsvar.diagnozStroka
            }
            return


def diagnoz():
    diagnozselect = ""
    for item in settingsvar.DiagnozRecomendaciya:
        diagnozselect = diagnozselect + item
    while ";" in diagnozselect:
        settingsvar.diagnozStroka = rest_api('/api/InterviewController/' + "0/" + diagnozselect + "/-1/0/0")
        if len(settingsvar.diagnozStroka) == 0:
            diagnozselect = diagnozselect[:len(diagnozselect) - 1]
            diagnozselect = diagnozselect[:diagnozselect.rfind(';')]
        else:
            break
    writediagnoz(settingsvar.diagnozStroka[0]['kodProtokola'], settingsvar.diagnozStroka[0]['nametInterview'])
    return


# --- Отображение на странице все параметоров установленого диагноза
def selectdiagnoz(request, select_kodProtokola, select_nametInterview):
    writediagnoz(select_kodProtokola, select_nametInterview)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def contentinterwiev(request):  # httpRequest
    api = rest_api('/api/ContentInterviewController/' + settingsvar.kodProtokola)
    settingsvar.html = 'diagnoz/contentinterwiev.html'
    data = {
        'compl': settingsvar.nametInterview,
        'detalinglist': api
    }
    return render(request, settingsvar.html, data)


def backdiagnoz(request):
    selectdiagnoz(request, settingsvar.kodProtokola, settingsvar.nametInterview)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


#  --- Кінець блоку  опитування

# --- Блок вибору медзакладу та профільного лікаря

def receptprofillmedzaklad(request):
    grupmedzaklad = []

    settingsvar.grupDiagnoz = rest_api('/api/MedGrupDiagnozController/' + "0/0/" + settingsvar.icddiagnoz)
    for item in settingsvar.grupDiagnoz:
        medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0')
        grupmedzaklad.append(medzaklad)

    html = 'diagnoz/receptionprofilzaklad.html'
    data = {
        'compl': 'Перелік профільних медзакладів',
        'detalinglist': grupmedzaklad
    }
    return render(request, html, context=data)


def selectdprofillikar(request, selected_edrpou):
    gruplikar = []
    Grupproflikar = rest_api('/api/ApiControllerDoctor/' + "0/" + selected_edrpou + "/0")
    for item in Grupproflikar:
        likarGrupDiagnoz = rest_api('/api/LikarGrupDiagnozController/' + item['kodDoctor'] + '/0')
        for icdgrdiagnoz in settingsvar.grupDiagnoz:
            for likargrdz in likarGrupDiagnoz:
                if likargrdz['icdGrDiagnoz'] in icdgrdiagnoz['icdGrDiagnoz'] and selected_edrpou in icdgrdiagnoz[
                    'edrpou']:
                    gruplikar.append(item)

    html = 'diagnoz/selectedprofillikar.html'
    data = {
        'compl': 'Перелік профільних лікарів',
        'detalinglist': gruplikar
    }
    return render(request, html, context=data)


def inputprofilpacient(request, selected_doctor):
    html = 'diagnoz/profilpacent.html'
    data = {
        'compl': 'Перелік профільних лікарів',
        'detalinglist': gruplikar
    }

    return render(request, html)


# --- кінець блоку
# ----Пациент

def receptfamilylikar(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def receptprofillikar(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def savediagnoz(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)




def pacientprofil(request):  # httpRequest
    return render(request, 'diagnoz/pacientprofil.html')


def pacientinterwiev(request):  # httpRequest
    return render(request, 'diagnoz/pacientinterwiev.html')


def pacientlistinterwiev(request):  # httpRequest
    return render(request, 'diagnoz/pacientlistinterwiev.html')


def pacientreceptionlikar(request):  # httpRequest
    return render(request, 'diagnoz/pacientreceptionlikar.html')


def pacientstanhealth(request):  # httpRequest
    return render(request, 'diagnoz/pacientstanhealth.html')


def likarprofil(request):  # httpRequest
    return render(request, 'diagnoz/likarprofil.html')


def likarinterweiv(request):  # httpRequest
    return render(request, 'diagnoz/likarinterweiv.html')


def likarlistinterweiv(request):  # httpRequest
    return render(request, 'diagnoz/likarlistinterweiv.html')


def likarreceptionpacient(request):  # httpRequest
    return render(request, 'diagnoz/likarreceptionpacient.html')


def likarvisitngdays(request):  # httpRequest
    return render(request, 'diagnoz/likarvisitngdays.html')


def likarworkdiagnoz(request):  # httpRequest
    return render(request, 'diagnoz/likarworkdiagnoz.html')


def likarlibdiagnoz(request):  # httpRequest
    return render(request, 'diagnoz/likarlibdiagnoz.html')


def adminlanguage(request):  # httpRequest
    return render(request, 'diagnoz/adminlanguage.html')




def contact(request):
    cnxn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=STARIC777;DATABASE=dbseam;Persist Security Info=False;Integrated Security=true;')
    cursor = cnxn.cursor()
    cursor.execute("")
    row = cursor.fetchone()
    context = {
        'NUM': str(row.NUM),
        'NAME': str(row.NAME)
    }
    return render(request, "hj/basic.html", context)
