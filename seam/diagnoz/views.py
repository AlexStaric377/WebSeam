import datetime
import json

import environ
import pyodbc
import requests
from django.shortcuts import render

from diagnoz import settingsvar
from .forms import PacientForm, AccountUserForm, ReestrAccountUserForm, LikarForm, SearchPacient


def rest_api(api_url, data, method):
    env = environ.Env()
    urls_api = env('urls_api')
    urls = urls_api + api_url

    match method:
        case 'GET':
            response = requests.get(urls)
        case 'POST':
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(urls, headers=headers, data=json.dumps(data))
        case 'PUT':
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(urls, headers=headers, data=json.dumps(data))
        case 'DEL':
            response = requests.delete(urls)
    stroka = []
    if len(response.content) > 1:
        stroka = json.loads(response.content)

    return stroka


#    return

def index(request):  # httpRequest
    return render(request, 'diagnoz/index.html')


def glavmeny(request):
    return render(request, 'diagnoz/glavmeny.html')

def reception(request):  # httpRequest
    settingsvar.kabinet = 'guest'
    return render(request, 'diagnoz/reception.html')


def pacient(request):  # httpRequest
    settingsvar.kabinet = 'pacient'
    settingsvar.setintertview = False
    return render(request, 'diagnoz/pacient.html')


def likar(request):  # httpRequest
    settingsvar.kabinet = 'likar'
    settingsvar.setintertview = False
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
    settingsvar.diagnozStroka = []
    interwievpacient = False
    return


def interwievcomplaint(request):
    cleanvars()
    settingsvar.nawpage = 'receptinterwiev'
    api = rest_api('api/ApiControllerComplaint/', '', 'GET')
    iduser = funciduser()
    data = {
        'complaintlist': api,
        'iduser': iduser,
        'backurl': 'reception'
    }
    return render(request, 'diagnoz/receptinterwiev.html', context=data)


# --- 2. Характер нездужання

def nextfeature(request, nextfeature_keyComplaint, nextfeature_name):
    settingsvar.DiagnozRecomendaciya.append(nextfeature_keyComplaint + ";")
    settingsvar.spselectnameDetailing.append(nextfeature_name)
    settingsvar.spisokselectDetailing.append(nextfeature_keyComplaint)
    settingsvar.strokagrdetaling = settingsvar.strokagrdetaling + nextfeature_keyComplaint + ";"
    settingsvar.spisokkeyinterview.append(nextfeature_keyComplaint + ";")
    settingsvar.feature_name = nextfeature_name
    settingsvar.listfeature = {}
    settingsvar.diagnozStroka = []
    if len(settingsvar.listfeature) <= 0:
        settingsvar.listfeature = rest_api('api/FeatureController/' + "0/" + nextfeature_keyComplaint + "/0/", '',
                                           'GET')
    iduser = funciduser()
    settingsvar.nawpage = 'nextfeature'
    html = 'diagnoz/nextfeature.html'
    data = {
        'compl': nextfeature_name,
        'next': '  Далі ',
        'iduser': iduser,
        'featurelist': settingsvar.listfeature
    }
    return render(request, html, context=data)


def featurespisok(request, featurespisok_keyComplaint, featurespisok_keyFeature, featurespisok_nameFeature):

    settingsvar.DiagnozRecomendaciya.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyinterview.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyfeature.append(featurespisok_keyFeature)
    settingsvar.spisoknamefeature.append(featurespisok_nameFeature)
    settingsvar.spselectnameDetailing.append(featurespisok_nameFeature)
    settingsvar.spisokselectDetailing.append(featurespisok_keyFeature)
    index = 0
    if len(settingsvar.listfeature) > 0:
        for item in settingsvar.listfeature:
            if featurespisok_keyFeature == item['keyFeature']:
                del settingsvar.listfeature[index]
                iduser = funciduser()
                data = {
                    'compl': settingsvar.feature_name,
                    'next': '  Далі ',
                    'iduser': iduser,
                    'featurelist': settingsvar.listfeature
                }
                return render(request, 'diagnoz/nextfeature.html', context=data)
            index = index + 1
    return render(request, 'diagnoz/errorfeature.html')


# --- 3. Деталізація характеру нездужання

def nextgrdetaling(request):
    nextstepgrdetaling()
    if len(settingsvar.nextstepdata) == 0:
        settingsvar.html = 'diagnoz/savediagnoz.html'
        backurl = funcbakurl()
        iduser = funciduser()
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'compl': 'Шановний користувач! За вашим запитом відсутні проведені опитування.',
            'backurl': backurl
        }
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Блок поиска и вывода описания диагноза

# --- функция распределения списков симптомов по локальным и групповым
def nextstepgrdetaling():
    settingsvar.detalingname = []
    settingsvar.listdetaling = {}
    settingsvar.spisokGrDetailing = []
    if len(settingsvar.spisokkeyfeature) > 0:
        for keyfeature in settingsvar.spisokkeyfeature:
            listkeyfeature = rest_api('api/DetailingController/' + "0/" + keyfeature + "/0/", '', 'GET')
            for itemkeyfeature in listkeyfeature:
                set = ""

                if itemkeyfeature['keyGrDetailing'] != None:
                    if len(itemkeyfeature['keyGrDetailing']) > 5:
                        settingsvar.detalingname.append(itemkeyfeature['nameDetailing'])
                        if itemkeyfeature['keyFeature'] in settingsvar.strokagrdetaling:
                            if itemkeyfeature['keyGrDetailing'] not in settingsvar.strokagrdetaling:
                                set = settingsvar.strokagrdetaling + itemkeyfeature['keyGrDetailing'] + ";"
                        else:
                            set = settingsvar.strokagrdetaling + itemkeyfeature['keyFeature'] + ";" + itemkeyfeature[
                            'keyGrDetailing'] + ";"
                        if len(set) != 0:
                            CmdStroka = rest_api('/api/InterviewController/' + "0/0/0/0/" + set, '', 'GET')
                            if len(CmdStroka) > 0:
                                settingsvar.strokagrdetaling = set
                                settingsvar.spisokGrDetailing.append(itemkeyfeature['keyGrDetailing'])
                                settingsvar.strokainterview = []
                                for itemgrDetail in CmdStroka:
                                    settingsvar.strokainterview.append(itemgrDetail['grDetail'])

                            else:
                                for itemgrDetail in settingsvar.strokainterview:
                                    if itemkeyfeature['keyGrDetailing'] + ";" in itemgrDetail:
                                        if itemkeyfeature['keyGrDetailing'] not in settingsvar.strokagrdetaling:
                                            settingsvar.strokagrdetaling = set
                                            settingsvar.spisokGrDetailing.append(itemkeyfeature['keyGrDetailing'])
                                            break
                    else:
                        settingsvar.spisoklistdetaling.append(itemkeyfeature)
                        if itemkeyfeature['keyFeature'] not in settingsvar.strokagrdetaling:
                            settingsvar.strokagrdetaling = settingsvar.strokagrdetaling + itemkeyfeature[
                                'keyFeature'] + ";"
                else:
                    settingsvar.spisoklistdetaling.append(itemkeyfeature)
                    if itemkeyfeature['keyFeature'] not in settingsvar.strokagrdetaling:
                        settingsvar.strokagrdetaling = settingsvar.strokagrdetaling + itemkeyfeature['keyFeature'] + ";"
            if len(settingsvar.spisoklistdetaling) > 0:
                enddetaling = 'enddetaling'
                settingsvar.detaling_feature_name = settingsvar.spisoknamefeature[0]
                settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                iduser = funciduser()
                settingsvar.nextstepdata = {
                    'nextdetali': enddetaling,
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
                    'next': '  Далі ',
                    'iduser': iduser,
                    'detalinglist': settingsvar.spisoklistdetaling
                }
                settingsvar.nawpage = 'detaling'
                settingsvar.html = 'diagnoz/detaling.html'
                del settingsvar.spisokkeyfeature[0]
                del settingsvar.spisoknamefeature[0]
                return
            if len(settingsvar.spisokGrDetailing) > 0:
                for itemgrdetaling in settingsvar.spisokGrDetailing:
                    settingsvar.rest_apiGrDetaling = rest_api(
                        '/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/", '', 'GET')
                    settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                    settingsvar.detaling_feature_name = settingsvar.spisoknamefeature[0]
                    settingsvar.itemdetalingname = settingsvar.detalingname[0]
                    iduser = funciduser()
                    settingsvar.nextstepdata = {
                        'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                        'next': '  Далі ',
                        'iduser': iduser,
                        'detalinglist': settingsvar.rest_apiGrDetaling
                    }
                    settingsvar.nawpage = 'grdetaling'
                    settingsvar.html = 'diagnoz/grdetaling.html'
                    del settingsvar.spisokGrDetailing[0]
                    del settingsvar.detalingname[0]
                    return
            else:
                del settingsvar.spisokkeyfeature[0]
            keyfeature = ""
        if len(keyfeature) == 0 and len(settingsvar.spisokkeyfeature) > 0: del settingsvar.spisokkeyfeature[0]
        return
    if len(settingsvar.DiagnozRecomendaciya) == 0:
        cleanvars()
        iduser = funciduser()
        settingsvar.nextstepdata = {
            'complaintlist': rest_api('api/ApiControllerComplaint/', '', 'GET'),
            'iduser': iduser
        }
        settingsvar.html = 'diagnoz/receptinterwiev.html'

    return


# ---  вибір деталізації симптому нездужання
def selectdetaling(request, select_kodDetailing, select_nameDetailing):
    settingsvar.spisokkeyinterview.append(select_kodDetailing + ";")
    settingsvar.spisokselectDetailing.append(select_kodDetailing)
    settingsvar.spselectnameDetailing.append(select_nameDetailing)
    index = 0
    settingsvar.nawpage = 'grdetaling'
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
        settingsvar.nawpage = 'detaling'
        iduser = funciduser()
        data = {
                'nextdetali': enddetaling,
                'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
                'next': '  Далі ',
            'iduser': iduser,
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
                settingsvar.nawpage = 'grdetaling'
                iduser = funciduser()
                data = {
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                    'next': '  Далі ',
                    'iduser': iduser,
                    'detalinglist': settingsvar.rest_apiGrDetaling
                }
                del settingsvar.rest_apiGrDetaling[index]
                return render(request, 'diagnoz/grdetaling.html', context=data)
            index = index + 1

    return render(request, 'diagnoz/grdetaling.html', context=data)


# --- кінець інтервью, пошук та виведення  попереднього діагнозу
def enddetaling(request):
    if len(settingsvar.spisokkeyfeature) > 0:
        if (settingsvar.viewdetaling == False and len(settingsvar.spisoklistdetaling) > 0):
            settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
            iduser = funciduser()
            data = {
                'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
                'next': '  Далі ',
                'iduser': iduser,
                'detalinglist': settingsvar.spisoklistdetaling
            }
            settingsvar.nawpage = 'detaling'
            settingsvar.viewdetaling = True
            del settingsvar.spisokkeyfeature[0]
            del settingsvar.spisoknamefeature[0]
            return render(request, 'diagnoz/detaling.html', context=data)
        else:
            settingsvar.spisoklistdetaling = []

        if len(settingsvar.spisokGrDetailing) > 0:
            for itemgrdetaling in settingsvar.spisokGrDetailing:
                settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                settingsvar.rest_apiGrDetaling = rest_api('/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/",
                                                          '', 'GET')
                settingsvar.itemdetalingname = settingsvar.detalingname[0]
                iduser = funciduser()
                data = {
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                    'next': '  Далі ',
                    'iduser': iduser,
                    'detalinglist': settingsvar.rest_apiGrDetaling
                }
                settingsvar.nawpage = 'grdetaling'
                del settingsvar.detalingname[0]
                del settingsvar.spisokGrDetailing[0]

                return render(request, 'diagnoz/grdetaling.html', context=data)
        else:
            if (settingsvar.itemkeyfeature == settingsvar.spisokkeyfeature[0]):
                del settingsvar.spisokkeyfeature[0]
                del settingsvar.spisoknamefeature[0]
        if len(settingsvar.spisokkeyfeature) > 0:
            nextstepgrdetaling()
            if len(settingsvar.spisokkeyfeature) == 0 and len(settingsvar.spisoklistdetaling) == 0 and len(
                    settingsvar.spisokGrDetailing) == 0:
                diagnoz()
        else:
            diagnoz()
    else:
        diagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def writediagnoz(select_kodProtokola, select_nametInterview):
    settingsvar.kodProtokola = select_kodProtokola
    settingsvar.nametInterview = select_nametInterview
    for item in settingsvar.diagnozStroka:
        if select_kodProtokola == item['kodProtokola']:
            api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
            apiicd = rest_api('/api/DiagnozController/' + api['kodDiagnoz'] + "/0/0", '', 'GET')
            settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
            api = rest_api('/api/RecommendationController/' + api['kodRecommend'] + "/0", '', 'GET')
            settingsvar.html = 'diagnoz/versiyadiagnoza.html'
            iduser = funciduser()
            settingsvar.nextstepdata = {
                'opis': item['opistInterview'],
                'http': item['uriInterview'],
                'rekomendaciya': api['contentRecommendation'],
                'compl': select_nametInterview,
                'detalinglist': settingsvar.diagnozStroka,
                'iduser': iduser
            }
            return


def diagnoz():
    diagnozselect = ""
    for item in settingsvar.DiagnozRecomendaciya:
        diagnozselect = diagnozselect + item
    while ";" in diagnozselect:
        settingsvar.diagnozStroka = rest_api('/api/InterviewController/' + "0/" + diagnozselect + "/-1/0/0", '', 'GET')
        if len(settingsvar.diagnozStroka) == 0:
            diagnozselect = diagnozselect[:len(diagnozselect) - 1]
            diagnozselect = diagnozselect[:diagnozselect.rfind(';')]
        else:
            break
    if len(settingsvar.diagnozStroka) > 0:
        writediagnoz(settingsvar.diagnozStroka[0]['kodProtokola'], settingsvar.diagnozStroka[0]['nametInterview'])
    else:
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.html = 'diagnoz/errorfeature.html'
        settingsvar.nextstepdata = {}
    return


# --- Отображение на странице все параметоров установленого диагноза
def selectdiagnoz(request, select_kodProtokola, select_nametInterview):
    writediagnoz(select_kodProtokola, select_nametInterview)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- виведення змісту інтервью
def contentinterwiev(request):  # httpRequest
    api = []
    if len(settingsvar.kodProtokola) > 0:
        api = rest_api('/api/ContentInterviewController/' + settingsvar.kodProtokola, '', 'GET')
    settingsvar.html = 'diagnoz/contentinterwiev.html'
    iduser = funciduser()
    data = {
        'compl': settingsvar.nametInterview,
        'detalinglist': api,
        'iduser': iduser,
        'backpage': settingsvar.nawpage
    }
    return render(request, settingsvar.html, data)


def backdiagnoz(request):
    selectdiagnoz(request, settingsvar.kodProtokola, settingsvar.nametInterview)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


#  --- Кінець блоку  опитування

# --- Блок вибору медзакладу та профільного лікаря
# --- вибір профільного медзакладу

def selectmedzaklad(statuszaklad):
    settingsvar.grupmedzaklad = []
    match statuszaklad:
        case "2":
            medzaklad = rest_api('/api/MedicalInstitutionController/' + '0/0/0/' + statuszaklad, '', 'GET')
            for item in medzaklad:
                if len(settingsvar.grupmedzaklad) == 0: settingsvar.grupmedzaklad.append(item)
                for itemmedzaklad in settingsvar.grupmedzaklad:
                    if item['edrpou'] not in itemmedzaklad['edrpou']:
                        settingsvar.grupmedzaklad.append(item)
        case "5":
            settingsvar.grupDiagnoz = rest_api('/api/MedGrupDiagnozController/' + "0/0/" + settingsvar.icddiagnoz, '',
                                               'GET')
            for item in settingsvar.grupDiagnoz:
                medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '', 'GET')
                if len(settingsvar.grupmedzaklad) == 0: settingsvar.grupmedzaklad.append(medzaklad)
                for itemmedzaklad in settingsvar.grupmedzaklad:
                    if medzaklad['edrpou'] not in itemmedzaklad['edrpou']:
                        settingsvar.grupmedzaklad.append(medzaklad)
    settingsvar.nawpage = 'receptionprofilzaklad'
    iduser = funciduser()
    settingsvar.html = 'diagnoz/receptionprofilzaklad.html'
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': 'Перелік профільних медзакладів',
        'detalinglist': settingsvar.grupmedzaklad
    }
    return


# --- вибір профільного медзакладу
def receptprofillmedzaklad(request):
    if settingsvar.kabinetitem == 'likarinterwiev':
        settingsvar.setintertview = True
        medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '', 'GET')
        settingsvar.namemedzaklad = medzaklad['name']
        settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
        settingsvar.mobtellikar = settingsvar.likar['telefon']
        saveselectlikar(settingsvar.pacient[0])
    else:
        selectmedzaklad('5')
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- вибір Амбулаторно-поліклінічного закладу до сімейного лікаря
def receptfamilylikar(request):
    selectmedzaklad('2')
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# --- Вибір лікаря у профільному мед закладі
def selectdprofillikar(request, selected_edrpou, selected_idstatus, selected_name):
    gruplikar = []
    settingsvar.namemedzaklad = selected_name
    Grupproflikar = rest_api('/api/ApiControllerDoctor/' + "0/" + selected_edrpou + "/0", '', 'GET')
    for item in Grupproflikar:
        match selected_idstatus:
            case "2":
                gruplikar.append(item)
            case "5":
                likarGrupDiagnoz = rest_api('/api/LikarGrupDiagnozController/' + item['kodDoctor'] + '/0', '', 'GET')
                for icdgrdiagnoz in settingsvar.grupDiagnoz:
                    for likargrdz in likarGrupDiagnoz:
                        if likargrdz['icdGrDiagnoz'] in icdgrdiagnoz['icdGrDiagnoz'] and selected_edrpou in \
                                icdgrdiagnoz[
                                    'edrpou']:
                            gruplikar.append(item)
                            break
                    break
    settingsvar.nawpage = 'selectedprofillikar'
    html = 'diagnoz/selectedprofillikar.html'
    iduser = funciduser()
    data = {
        'iduser': iduser,
        'compl': 'Перелік профільних лікарів',
        'detalinglist': gruplikar
    }
    return render(request, html, context=data)


# --- Функція повернення до початку опитування
def funcbakurl():
    bakurl = 'reception'
    match settingsvar.kabinet:
        case "guest":
            bakurl = 'reception'
        case "pacient":
            bakurl = 'pacient'
        #        case "interwiev" "listinterwiev":
        #            bakurl = 'kabinetpacient'
        case "likar":
            bakurl = 'likar'
        case 'likarinterwiev':
            bakurl = 'likarinterweiv'
        case 'likarlistinterwiev':
            bakurl = 'likarlistinterwiev'
    return bakurl


# --- Функція повернення до початку опитування
def funciduser():
    iduser = 'Анонімний відвідувач'
    match settingsvar.kabinet:
        case "guest":
            iduser = 'Анонімний відвідувач'
        case "pacient":
            iduser = 'Кабінет пацієнта'
        case "likar":
            iduser = 'Кабінет лікаря'
    return iduser


# --- Функція повернення до поточнлї сторінки при перегляді змісту   опитування
def funcbackpage():
    backpage = 'backdiagnoz'
    match settingsvar.kabinet:
        case "guest":
            backpage = settingsvar.nawpage
        case "pacient":
            backpage = settingsvar.nawpage
        case "likar":
            backpage = settingsvar.nawpage
    return backpage

# --- функція формування запиту на підтвердження збереження вибору лікаря
def saveselectlikar(pacient):
    backurl = funcbakurl()
    iduser = funciduser()
    if settingsvar.setintertview == True:
        settingsvar.html = 'diagnoz/finishreception.html'
        if backurl == 'pacient' or backurl == 'likar' or bakurl == 'likarinterweiv':
            settingsvar.html = 'diagnoz/finishinterviewpacient.html'
            if backurl == 'likar' or bakurl == 'likarinterweiv':
                settingsvar.nawpage = 'receptprofillmedzaklad'
                settingsvar.nextstepdata = {
                    'iduser': iduser,
                    'pacient': 'Увага! сформовано попередній діаноз на прийомі у лікаря.',
                    'shapka': 'Пацієнт: ' + pacient['name'] + " " + pacient['surname'],
                    'medzaklad': settingsvar.namemedzaklad,
                    'likar': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
                    'datereception': 'Дата прийому: ' + settingsvar.datereception,
                    'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
                    'podval': 'Ви підтверджуєте збереження опитування?',
                    'backurl': backurl
                }
            else:
                settingsvar.nextstepdata = {
                    'iduser': iduser,
                'pacient': 'Увага! ' + pacient['name'] + " " + pacient['surname'],
                    'shapka': 'Ви сформували запит на прийом до лікаря.',
                    'medzaklad': settingsvar.namemedzaklad,
                    'likar': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
                    'datereception': 'Дата прийому: ' + settingsvar.datereception,
                    'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
                    'podval': 'Ви підтверджуєте свій вибір?',
                    'backurl': backurl
                }
    else:
        settingsvar.html = 'diagnoz/savediagnoz.html'
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'compl': 'Шановний користувач! Ваш профіль збережено.',
            'backurl': backurl
        }
    return


# --- введення профілю пацієнта для запису на прийом до лікаря
def inputprofilpacient(request, selected_doctor):
    settingsvar.namelikar = ""
    settingsvar.mobtellikar = ""
    settingsvar.kodDoctor = selected_doctor
    settingsvar.setintertview = True
    CmdStroka = rest_api('/api/ApiControllerDoctor/' + selected_doctor + "/0/0", '', 'GET')
    if len(CmdStroka) > 0:
        settingsvar.namelikar = CmdStroka['name'] + " " + CmdStroka['surname']
        settingsvar.mobtellikar = CmdStroka['telefon']
    match settingsvar.kabinet:
        case "guest":
            settingsvar.html = 'diagnoz/pacientprofil.html'
            pacientprofil(request)
            form = PacientForm()
            if settingsvar.html == 'diagnoz/pacientprofil.html':
                settingsvar.nextstepdata = {'form': form}
        case "pacient":
            saveselectlikar(settingsvar.pacient)

        case "likar":
            saveselectlikar(settingsvar.pacient)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# -----------------------------------------------------------------------
# --- Зберегти протокол опитування
# --- визначення нового коду протоколу опитування
def SelectNewKodComplInteriew():
    CmdStroka = []
    indexcmp = "CMP.000000000001"
    CmdStroka = rest_api('/api/CompletedInterviewController/' + "0/1", '', 'GET')

    if len(CmdStroka) > 0:
        kodCompl = CmdStroka['kodComplInterv']
        indexdia = int(kodCompl[5:16])
        repl = "000000000000"
        indexcmp = "CMP." + repl[0: len(repl) - len(str(indexdia))] + str(indexdia + 1)

    return indexcmp;


# --- визначення нового коду протоколу опитування
def addCompletedInterview():
    Numberstroka = 0
    for item in settingsvar.spselectnameDetailing:
        json = {'id': 0,
                'KodComplInterv': settingsvar.kodComplInterv,
                'numberstr': Numberstroka,
                'KodDetailing': settingsvar.spisokselectDetailing[Numberstroka],
                'DetailsInterview': item
                }
        saveintreview = rest_api('/api/CompletedInterviewController/', json, 'POST')
        Numberstroka = Numberstroka + 1
    return


# --- Додати протокол опитування до колекції опитувань
def addColectionInterview():
    details = ""
    settingsvar.dateInterview = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    settingsvar.kodComplInterv = SelectNewKodComplInteriew()
    for item in settingsvar.spisokselectDetailing:
        details = details + item + ';'
    json = {'id': 0,
            'kodDoctor': settingsvar.kodDoctor,
            'kodPacient': settingsvar.kodpacienta,
            'dateInterview': settingsvar.dateInterview,
            'DateDoctor': settingsvar.datedoctor,
            'kodProtokola': settingsvar.kodProtokola,
            'detailsInterview': details,
            'resultDiagnoz': settingsvar.resultDiagnoz,
            'kodComplInterv': settingsvar.kodComplInterv,
            'nameInterview': settingsvar.nametInterview
            }

    saveintreview = rest_api('/api/ColectionInterviewController/', json, 'POST')
    return


# --- збереження попереднього діагнозу протоколу опитування
def savediagnoz(request):
    # --- додати проткол опитування
    addColectionInterview()
    # ---  Додати опитування
    addCompletedInterview()
    errorprofil('Шановний користувач! Ваш протокол опитування та попередній діагноз збережено.')
    return render(request, settingsvar.html, settingsvar.nextstepdata)


# --- кінець  готового блоку
#-------------------------------------------------------------------------
# ---------  Кабінет Пациента

# ---- Функція формування облікового запису  при реєстрації нового користувача (пацієнт або лікар)
def funcaddaccount(login, password):
    details = 'false'
    settingsvar.dateInterview = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    settingsvar.jsonstroka = {'Id': 0,
                              'IdUser': newpacientprofil(),
                              'IdStatus': '2',
                              'Login': login,
                              'Password': password,
                              'AccountCreatDate': settingsvar.dateInterview,
                              'Subscription': details,
                              }
    return
# --------------------------
# Реєстрація входу до кабінету пацієнта

def reestraccountuser(request):
    settingsvar.html = 'diagnoz/reestraccountuser.html'
    settingsvar.readprofil = False

    if request.method == 'POST':
        if settingsvar.setReestrAccount == False:
            formaccount = ReestrAccountUserForm(request.POST)
            if formaccount.data['password'] != formaccount.data['dwpassword']:
                settingsvar.setReestrAccount = False
                errorprofil('Шановний користувач! Введені паролі не співпадають')
            else:

                json = "0/" + formaccount.data['login'] + "/" + formaccount.data['password'] + '/0'
                Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                if len(Stroka) > 0:
                    settingsvar.setReestrAccount = False
                    errorprofil('Шановний користувач! Введені паролі не співпадають')
                else:
                    funcaddaccount(formaccount.data['login'], formaccount.data['password'])
                    settingsvar.setReestrAccount = True
                    settingsvar.html = 'diagnoz/pacientprofil.html'
                    form = PacientForm()
                    settingsvar.html == 'diagnoz/pacientprofil.html'
                    settingsvar.nextstepdata = {
                        'form': form,
                        'next': settingsvar.readprofil
                    }
        else:
            pacientprofil(request)

    else:
        if settingsvar.setReestrAccount == False:
            settingsvar.readprofil = False
            formreestraccount = ReestrAccountUserForm()
            settingsvar.nextstepdata = {
                'form': formreestraccount,
                'backurl': 'kabinetpacient',
                'reestrinput': 'Реєстрація в кабінеті пацієнта',
            }
        else:
            pacientprofil(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

def accountuser(request):

    settingsvar.html = 'diagnoz/accountuser.html'
    if settingsvar.setpost == False:
        if request.method == 'POST':
            if settingsvar.searchaccount == True:
                form = SearchPacient(request.POST)
                settingsvar.formsearch = form.data
                funcsearchpacient(settingsvar.formsearch)
            else:
                formaccount = AccountUserForm(request.POST)
                json = "0/" + formaccount.data['login'] + "/" + formaccount.data['password'] + '/0'
                Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                if len(Stroka) > 0:
                    match settingsvar.kabinetitem:
                        case "profil" | "pacient" | "interwiev" | 'listinterwiev':
                            settingsvar.kodPacient = Stroka['idUser']
                            settingsvar.pacient = rest_api(
                                '/api/PacientController/' + settingsvar.kodPacient + '/0/0/0/0',
                                                       '', 'GET')

                            if len(settingsvar.pacient) > 0:
                                settingsvar.setpost = True
                                settingsvar.readprofil = True
                                formpacient = PacientForm(initial=settingsvar.pacient)
                                settingsvar.nextstepdata = {
                                'form': formpacient,
                                'next': settingsvar.readprofil
                                }
                                settingsvar.html = 'diagnoz/pacientprofil.html'
                            else:
                                errorprofil(
                                'Шановний користувач! За вказаним обліковим записом профіль пацієнта не знайдено.')
                        case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
                            settingsvar.kodLikar = Stroka['idUser']
                            settingsvar.likar = rest_api('/api/ApiControllerDoctor/' + settingsvar.kodLikar + '/0/0',
                                                         '', 'GET')
                            if len(settingsvar.likar) > 0:
                                settingsvar.setpost = True
                                settingsvar.readprofil = True
                                settingsvar.setpostlikar = True
                                settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
                                medzaklad = rest_api(
                                    '/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '',
                                    'GET')
                                settingsvar.namemedzaklad = medzaklad['name']
                                settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
                                settingsvar.mobtellikar = settingsvar.likar['telefon']
                                if settingsvar.kabinetitem != 'likarlistinterwiev':
                                    search_pacient()
                                else:
                                    listlikar()
                            else:
                                errorprofil(
                                'Шановний користувач! За вказаним обліковим записом профіль лікаря не знайдено.')
                else:
                    errorprofil('Шановний користувач! Невірно введено номер телефону або пароль.')
        else:
            cab = 'Кабінет пацієнта'
            if settingsvar.kabinetitem == "likar" or settingsvar.kabinetitem == 'likarinterwiev':
                cab = 'Кабінет лікаря'

            settingsvar.readprofil = False
            formaccount = AccountUserForm()
            settingsvar.nextstepdata = {
                'form': formaccount,
                'compl': 'Зареєструватися',
                'reestrinput': cab,
            }
    else:
        match settingsvar.kabinetitem:
            case 'profil':
                settingsvar.readprofil = True
                iduser = funciduser()
                formpacient = PacientForm(initial=settingsvar.pacient)
                settingsvar.nextstepdata = {
                    'form': formpacient,
                    'next': settingsvar.readprofil
                }
                settingsvar.html = 'diagnoz/pacientprofil.html'

            case 'interwiev':
                iduser = funciduser()
                settingsvar.html = 'diagnoz/receptinterwiev.html'
                api = rest_api('api/ApiControllerComplaint/', '', 'GET')
                settingsvar.nextstepdata = {
                    'complaintlist': api,
                    'iduser': iduser
                }
            case 'listinterwiev':
                iduser = funciduser()
                settingsvar.html = 'diagnoz/pacientlistinterwiev.html'
                listapi = []
                listapi = rest_api('api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacient, '', 'GET')
                if len(listapi) > 0:
                    settingsvar.nextstepdata = {
                        'iduser': iduser,
                        'complaintlist': listapi
                    }
                else:
                    errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')

            case 'likar':
                settingsvar.readprofil = True
                iduser = funciduser()
                formlikar = LikarForm(initial=settingsvar.likar)
                settingsvar.nextstepdata = {
                    'form': formlikar,
                    'next': settingsvar.readprofil
                }
                settingsvar.html = 'diagnoz/likarprofil.html'
            case 'likarinterwiev':
                if len(settingsvar.pacient) > 0:
                    shablonlikar(settingsvar.pacient[0])
                else:
                    settingsvar.searchaccount = True
                    search_pacient()
            case 'likarlistinterwiev':
                listlikar()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- пошуку даних пацієнта
def funcsearchpacient(formsearch):
    if len(formsearch['name']) > 0 and len(formsearch['surname']) > 0 and len(
            formsearch['telefon']) > 0:
        json = "0/0/" + formsearch['name'] + "/" + formsearch['surname'] + '/' + formsearch[
            'telefon']
    if len(formsearch['name']) > 0 and len(formsearch['surname']) > 0 and len(
            formsearch['telefon']) == 0:
        json = "0/0/" + formsearch['name'] + "/" + formsearch['surname'] + '/0'
    if len(formsearch['name']) > 0 and len(formsearch['surname']) == 0 and len(
            formsearch['telefon']) == 0:
        json = "0/0/" + formsearch['name'] + '/0/0'
    if len(formsearch['name']) == 0 and len(formsearch['surname']) == 0 and len(
            formsearch['telefon']) > 0:
        json = "0/0/0/0/" + formsearch['telefon']
    if len(formsearch['name']) == 0 and len(formsearch['surname']) > 0 and len(
            formsearch['telefon']) > 0:
        json = "0/0/0/" + formsearch['surname'] + '/' + formsearch['telefon']
    settingsvar.pacient = rest_api('api/PacientController/' + json, '', 'GET')

    if len(settingsvar.pacient) > 0:
        profilpacient = {}
        profilpacient = settingsvar.pacient[0]
        settingsvar.kodPacienta = profilpacient['kodPacient']
        shablonlikar(profilpacient)
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні дані про пацієнта.')

    return


def kabinetpacient(request):
    settingsvar.html = 'diagnoz/pacientprofil.html'
    form = PacientForm()
    settingsvar.nextstepdata = {
        'form': form,
        'next': settingsvar.readprofil
    }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# --- Створення нового коду профілю пацієнта
def newpacientprofil():
    CmdStroka = []
    indexcmp = "PCN.000000001"
    CmdStroka = rest_api('/api/PacientController/0/0/0/0/0', '', 'GET')

    if len(CmdStroka) > 0:
        kodPacient = CmdStroka['kodPacient']
        indexdia = int(kodPacient[5:14])
        repl = "000000000"
        settingsvar.kodPacient = "PCN." + repl[0: len(repl) - len(str(indexdia))] + str(indexdia + 1)

    return settingsvar.kodPacient


# --- Введення профілю пацієнта
def Pacientinitial():
    json = {'kodPacient': '',
            'kodKabinet': '',
            'age': '',
            'weight': '',
            'growth': '',
            'gender': '',
            'tel': '',
            'email': '',
            'name': '',
            'surname': '',
            'pind': '',
            'profession': '',

            }
    return json


def pacientprofil(request):  # httpRequest

    settingsvar.html = 'diagnoz/pacientprofil.html'
    if settingsvar.kabinetitem != 'likarinterwiev': settingsvar.kabinetitem = 'profil'

    if request.method == 'POST':
        form = PacientForm(request.POST)
        #       if form.is_valid():
        json = {'id': 0,
                'KodPacient': newpacientprofil(),
                'KodKabinet': "",
                'Age': form.data['age'],
                'Weight': form.data['weight'],
                'Growth': form.data['growth'],
                'Gender': form.data['gender'],
                'Tel': form.data['tel'],
                'Email': form.data['email'],
                'Name': form.data['name'],
                'Surname': form.data['surname'],
                'Pind': form.data['pind'],
                'Profession': form.data['profession']
                }

        # --- записати в Бд введенний профіль
        settingsvar.pacient = rest_api('/api/PacientController/', json, 'POST')
        if len(settingsvar.pacient) > 0:
            if settingsvar.readprofil != False:
                saveselectlikar(settingsvar.pacient)
            else:
                if settingsvar.kabinetitem == 'likarinterwiev':
                    shablonlikar(settingsvar.pacient)
                else:
                    settingsvar.setpost = True
                    errorprofil('Шановний користувач!  Ваш обліковий запис та профіль збережено.')
        else:
            errorprofil('Шановний користувач! Похибка на серевері. Ваш профіль не збережено.')
    else:

        form = PacientForm()
        settingsvar.nextstepdata = {

            'form': form,
            'next': False
        }
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Функція формування реквізитів профілю пацієнта для відображення на вебсайті
def shablonlikar(profilpacient):
    settingsvar.setpostlikar = True
    settingsvar.readprofil = True

    iduser = funciduser()
    backurl = funcbakurl()
    api = rest_api('api/ApiControllerComplaint/', '', 'GET')
    settingsvar.html = 'diagnoz/receptinterwiev.html'
    tel = ''
    mail = ''
    pind = ''
    if profilpacient['tel'] != None: tel = profilpacient['tel']
    if profilpacient['email'] != None: mail = profilpacient['email']
    if profilpacient['pind'] != None: pind = profilpacient['pind']
    tel_email_pind = 'Тел.: ' + tel + ' Ел.Пошта: ' + mail + ' Пошт.індекс: ' + pind
    settingsvar.nextstepdata = {
        'complaintlist': api,
        'likar': settingsvar.setpostlikar,
        'iduser': iduser,
        'backurl': backurl,
        'pacient': 'Пацієнт: ' + profilpacient['profession'] + ' ' + profilpacient['name'] + " " + profilpacient[
            'surname'],
        'age_weight_growth': 'Вік: ' + str(profilpacient['age']) + 'р. Вага: ' + str(
            profilpacient['weight']) + 'кг. Зріст: ' + str(profilpacient['growth']) + 'см.',
        'tel_email_pind': tel_email_pind,
        'piblikar': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
        'medzaklad': settingsvar.namemedzaklad
    }
    return


# ----- Функция виведення діагностичного повідомлення
def errorprofil(compl):
    settingsvar.html = 'diagnoz/savediagnoz.html'
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': compl,
        'backurl': backurl
    }
    return

# ---  Збереження запису до лікаря в історії пацієнта
def addReceptionPacient():
    json = {'id': 0,
            'KodPacient': settingsvar.kodPacienta,
            'KodDoctor': settingsvar.kodDoctor,
            'DateInterview': settingsvar.dateInterview,
            'KodComplInterv': settingsvar.kodComplInterv,
            'KodProtokola': settingsvar.kodProtokola,
            'TopictVizita': 'Підтвердження попереднього діагнозу, призначення плану лікування.',
            }
    # --- записати в Бд
    saveprofil = rest_api('/api/LifePacientController/', json, 'POST')
    return


# ---  Збереження запису до лікаря протоколу опитування пацієнта
def addReceptionLikar():
    json = {'id': 0,
            'KodPacient': settingsvar.kodPacienta,
            'KodDoctor': settingsvar.kodDoctor,
            'DateDoctor': settingsvar.datereception,
            'DateInterview': settingsvar.dateInterview,
            'KodComplInterv': settingsvar.kodComplInterv,
            'KodProtokola': settingsvar.kodProtokola,
            'TopictVizita': 'Підтвердження попереднього діагнозу, призначення плану лікування.',
            }

    # --- записати в Бд
    saveprofil = rest_api('/api/RegistrationAppointmentController/', json, 'POST')
    return


# --- Збереження протоколу опитування та запису до лікаря
def saveraceptionlikar(request):  # httpRequest
    # --- додати проткол опитування
    addColectionInterview()
    # ---  Додати опитування
    addCompletedInterview()
    # ---  Додати запис до лікаря в історії пацієнта
    addReceptionPacient()
    # ---  Додати запис до лікаря протоколу опитування пацієнта
    addReceptionLikar()
    backurl = funcbakurl()
    iduser = funciduser()
    settingsvar.nawpage = 'saveraceptionlikar'
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'finishtext': 'Шановний користувач! Ваш протокол опитування,  попередній діагноз та запис до лікаря збережено.',
        'backurl': backurl
    }
    settingsvar.html = 'diagnoz/saveraceptionlikar.html'
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Профіль пацієнта
def profilpacient(request):  # httpRequest
    cleanvars()
    settingsvar.nawpage = 'pacientprofil'
    settingsvar.kabinetitem = 'profil'
    if settingsvar.setpost == False:
        accountuser(request)
    else:
        settingsvar.html = 'diagnoz/pacientprofil.html'
        if settingsvar.readprofil == True:
            settingsvar.html = 'diagnoz/pacient.html'
        settingsvar.readprofil = True
        iduser = funciduser()
        formpacient = PacientForm(initial=settingsvar.pacient)
        settingsvar.nextstepdata = {
            'form': formpacient,
            'next': settingsvar.readprofil
        }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Провести опитування пациєнта в особистому кабінеті
def pacientinterwiev(request):  # httpRequest
    cleanvars()
    settingsvar.readprofil = False
    settingsvar.nawpage = 'receptinterwiev'
    settingsvar.kabinetitem = 'interwiev'
    if settingsvar.setpost == False:
        accountuser(request)
    else:
        iduser = funciduser()
        api = rest_api('api/ApiControllerComplaint/', '', 'GET')
        settingsvar.html = 'diagnoz/receptinterwiev.html'
        settingsvar.nextstepdata = {
            'complaintlist': api,
            'iduser': iduser,
            'backurl': 'pacient'
        }
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Профіль проведеного інтервью
def profilinterview(request, selected_protokol):  # httpRequest
    likarName = ""
    dateint = ""
    select_dateDoctor = ""
    settingsvar.nawpage = 'pacientlistinterwiev'
    settingsvar.kodProtokola = selected_protokol
    backurl = 'pacientlistinterwiev'
    iduser = funciduser()
    for item in settingsvar.listapi:
        if selected_protokol == item['kodProtokola']:
            if (item['dateDoctor'] != None):
                select_dateDoctor = item['dateDoctor']
            dateint = item['dateInterview']
            if len(item['kodDoctor']) > 0:
                doc = rest_api('api/ApiControllerDoctor/' + item['kodDoctor'] + '/0/0', '', 'GET')
                likarName = doc['name'] + ' ' + doc['surname'] + ' Телефон: ' + doc['telefon']
            break
    depend = rest_api('api/DependencyDiagnozController/' + '0/' + selected_protokol + '/0', '', 'GET')
    recommend = rest_api('api/RecommendationController/' + depend['kodRecommend'] + '/0', '', 'GET')
    diagnoz = rest_api('api/DiagnozController/' + depend['kodDiagnoz'] + '/0/0', '', 'GET')
    settingsvar.html = 'diagnoz/profilinterview.html'
    settingsvar.nextstepdata = {
        'pacient': 'Пацієнт:        ' + settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname'],
        'likar': 'Лікар:          ' + likarName,
        'dateinterv': 'Дата опитування: ' + dateint,
        'datereception': 'Дата прийому:   ' + select_dateDoctor,
        'diagnoz': 'Попередній діагноз: ' + diagnoz['nameDiagnoza'],
        'recomendaciya': 'Рекомендації:   ' + recommend['contentRecommendation'],
        'urlinet': 'Опис в інтернеті:   ' + diagnoz['uriDiagnoza'],
        'iduser': iduser

    }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


#--- Перегляд проведених інтервью

def pacientlistinterwiev(request):  # httpRequest
    cleanvars()
    settingsvar.readprofil = False
    backurl = funcbakurl()
    settingsvar.nawpage = 'receptinterwiev'
    settingsvar.kabinetitem = 'listinterwiev'
    if settingsvar.setpost == False:
        accountuser(request)

    else:
        iduser = funciduser()
        settingsvar.html = 'diagnoz/pacientlistinterwiev.html'

        settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacient, '', 'GET')
        if len(settingsvar.listapi) > 0:
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'complaintlist': settingsvar.listapi,
                'backurl': backurl
            }
        else:
            errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return render(request, settingsvar.html, settingsvar.nextstepdata )


def pacientreceptionlikar(request):  # httpRequest
    return render(request, 'diagnoz/pacientreceptionlikar.html')


def pacientstanhealth(request):  # httpRequest
    return render(request, 'diagnoz/pacientstanhealth.html')


def receptprofillikar(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --------- Лікар
# --- Реєстрація до кабінету лікаря
# ---------   Профіль лікаря

def likarprofil(request):  # httpRequest
    cleanvars()
    settingsvar.nawpage = 'likarprofil'
    settingsvar.kabinetitem = 'likar'
    if settingsvar.setpostlikar == False:
        accountuser(request)
    else:
        settingsvar.setpostlikar = False
        settingsvar.html = 'diagnoz/likar.html'
        settingsvar.readprofil = True
        iduser = funciduser()
        settingsvar.nextstepdata = {}

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Функція пошуку пацієнта в БД для проведення опитування
def search_pacient():
    iduser = funciduser()
    formsearch = SearchPacient()
    settingsvar.nextstepdata = {
        'form': formsearch,
        'compl': 'Зареєструвати пацієнта',
        'reestrinput': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
        'medzaklad': settingsvar.namemedzaklad
    }
    settingsvar.html = 'diagnoz/searchpacient.html'
    return

# --------- Прведення опитування лікарем
def likarinterweiv(request):  # httpRequest
    cleanvars()
    settingsvar.readprofil = False
    settingsvar.nawpage = 'likarinterwiev'
    settingsvar.kabinetitem = 'likarinterwiev'
    if settingsvar.setpostlikar == False:
        accountuser(request)
    else:
        # --- пошук даних пацієнта для проведення опитування
        if settingsvar.search == False:
            if request.method == 'POST':
                form = SearchPacient(request.POST)
                settingsvar.formsearch = form.data
                funcsearchpacient(settingsvar.formsearch)
                settingsvar.search = True
            else:
                settingsvar.setpost = False
                search_pacient()
        else:
            funcsearchpacient(settingsvar.formsearch)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listlikar():
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.html = 'diagnoz/likarlistinterweiv.html'
    settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/' + settingsvar.kodDoctor + '/0', '', 'GET')
    if len(settingsvar.listapi) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'backurl': backurl
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return

def likarlistinterweiv(request):  # httpRequest
    cleanvars()
    settingsvar.readprofil = False
    backurl = funcbakurl()
    settingsvar.nawpage = 'likarlistinterwiev'
    settingsvar.kabinetitem = 'likarlistinterwiev'
    if settingsvar.setpost == False:
        accountuser(request)
    else:
        listlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


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
