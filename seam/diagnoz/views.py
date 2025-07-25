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
    if settingsvar.kabinet == 'guest' and settingsvar.html != 'diagnoz/glavmeny.html':
        settingsvar.nawpage = ''
        settingsvar.html = 'diagnoz/glavmeny.html'
    else:
        settingsvar.kabinet = 'guest'
        settingsvar.likar = {}
        settingsvar.pacient = {}
        settingsvar.setintertview = False
        settingsvar.kabinetitem = 'guest'
        interwievcomplaint(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def pacient(request):  # httpRequest
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev') and len(
            settingsvar.likar) > 0:
        errorprofil('Шановний користувач! Активний кабінет пацієнта. Вхід до кабінету лікаря неможливий.')
    else:
        settingsvar.kabinet = 'pacient'
        settingsvar.setintertview = False
        settingsvar.html = 'diagnoz/pacient.html'
        settingsvar.nextstepdata = {}
        settingsvar.likar = {}
        settingsvar.setpost = False
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Вийти з кабінету
def exitkabinet(request):
    cleanvars()
    settingsvar.kabinet = ''
    settingsvar.kabinetitem = ''
    settingsvar.likar = {}
    settingsvar.pacient = {}
    settingsvar.formsearch = {}
    settingsvar.html = 'diagnoz/glavmeny.html'
    settingsvar.nextstepdata = {}
    settingsvar.setpostlikar = False
    settingsvar.setpost = False
    settingsvar.searchaccount = False
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

def likar(request):  # httpRequest
    if ((
            settingsvar.kabinet == 'pacient' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listinterwiev')
            and len(settingsvar.pacient) > 0):
        errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
    else:
        settingsvar.kabinet = 'likar'
        settingsvar.html = 'diagnoz/likar.html'
        settingsvar.setintertview = False
        settingsvar.nextstepdata = {}
        settingsvar.pacient = {}
        settingsvar.setpost = False
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


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
    settingsvar.kodProtokola = ""
    settingsvar.setintertview = False
    return


def interwievcomplaint(request):
    if settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'likarinterwiev':
        shablonlikar(settingsvar.pacient)
    else:
        cleanvars()
        match settingsvar.kabinet:
            case 'guest':
                settingsvar.setpostlikar = False
                iduser = 'Реєстратура: ' + funciduser()
            case 'pacient' | 'interwiev' | 'likar' | 'likarinterwiev':
                settingsvar.setpostlikar = True
                iduser = funciduser()
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.html = 'diagnoz/receptinterwiev.html'
        api = rest_api('api/ApiControllerComplaint/', '', 'GET')

        settingsvar.nextstepdata = {
        'complaintlist': api,
        'iduser': iduser,
        'backurl': 'reception'
        }
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


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
    settingsvar.html = 'diagnoz/nextfeature.html'

    if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['featurelist'] = settingsvar.listfeature
    settingsvar.nextstepdata['next'] = '  Далі '
    settingsvar.nextstepdata['compl'] = nextfeature_name
    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
    settingsvar.nextstepdata['iduser'] = iduser

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def featurespisok(request, featurespisok_keyComplaint, featurespisok_keyFeature, featurespisok_nameFeature):

    settingsvar.DiagnozRecomendaciya.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyinterview.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyfeature.append(featurespisok_keyFeature)
    settingsvar.spisoknamefeature.append(featurespisok_nameFeature)
    settingsvar.spselectnameDetailing.append(featurespisok_nameFeature)
    settingsvar.spisokselectDetailing.append(featurespisok_keyFeature)
    settingsvar.keyFeature = featurespisok_keyFeature
    funcfeature()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backfeature(request):
    funcfeature()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funcfeature():
    index = 0
    settingsvar.nextstepdata = {}
    settingsvar.html = 'diagnoz/errorfeature.html'
    if len(settingsvar.listfeature) > 0:
        for item in settingsvar.listfeature:
            if settingsvar.keyFeature == item['keyFeature']:
                del settingsvar.listfeature[index]
                iduser = funciduser()
                settingsvar.nawpage = 'backfeature'
                if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
                settingsvar.nextstepdata['featurelist'] = settingsvar.listfeature
                settingsvar.nextstepdata['next'] = '  Далі '
                settingsvar.nextstepdata['compl'] = settingsvar.feature_name
                settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
                settingsvar.nextstepdata['iduser'] = iduser
                settingsvar.html = 'diagnoz/nextfeature.html'
                break
            index = index + 1
    return


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

                shablonpacient(settingsvar.pacient)
                settingsvar.nextstepdata['detalinglist'] = settingsvar.spisoklistdetaling
                settingsvar.nextstepdata['compl'] = settingsvar.feature_name + ", " + settingsvar.detaling_feature_name
                settingsvar.nextstepdata['next'] = '  Далі '
                settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
                settingsvar.nextstepdata['iduser'] = iduser
                settingsvar.nawpage = 'receptinterwiev'
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

                    if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
                    settingsvar.nextstepdata['detalinglist'] = settingsvar.rest_apiGrDetaling
                    settingsvar.nextstepdata[
                        'compl'] = settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname
                    settingsvar.nextstepdata['next'] = '  Далі '
                    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
                    settingsvar.nextstepdata['iduser'] = iduser
                    settingsvar.nawpage = 'receptinterwiev'
                    settingsvar.html = 'diagnoz/grdetaling.html'
                    del settingsvar.spisokGrDetailing[0]
                    del settingsvar.detalingname[0]
                    return
            else:
                del settingsvar.spisokkeyfeature[0]
            keyfeature = ""
        if len(keyfeature) == 0 and len(settingsvar.spisokkeyfeature) > 0: del settingsvar.spisokkeyfeature[0]
        return
    else:
        settingsvar.DiagnozRecomendaciya = []
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
    settingsvar.nawpage = 'receptinterwiev'
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
        settingsvar.nawpage = 'receptinterwiev'
        shablondetaling()

        return render(request, settingsvar.html, context=settingsvar.nextstepdata)

    return render(request, 'diagnoz/grdetaling.html', context=settingsvar.nextstepdata)


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
                settingsvar.nawpage = 'receptinterwiev'
                shablongrdetaling()
                del settingsvar.rest_apiGrDetaling[index]
                return render(request, settingsvar.html, context=settingsvar.nextstepdata)
            index = index + 1

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- кінець інтервью, пошук та виведення  попереднього діагнозу
def enddetaling(request):
    if len(settingsvar.spisokkeyfeature) > 0:
        if (settingsvar.viewdetaling == False and len(settingsvar.spisoklistdetaling) > 0):
            settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
            shablondetaling()
            settingsvar.nawpage = 'receptinterwiev'
            settingsvar.viewdetaling = True
            del settingsvar.spisokkeyfeature[0]
            del settingsvar.spisoknamefeature[0]
            return render(request, settingsvar.html, context=settingsvar.nextstepdata)
        else:
            settingsvar.spisoklistdetaling = []

        if len(settingsvar.spisokGrDetailing) > 0:
            for itemgrdetaling in settingsvar.spisokGrDetailing:
                settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                settingsvar.rest_apiGrDetaling = rest_api('/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/",
                                                          '', 'GET')
                settingsvar.itemdetalingname = settingsvar.detalingname[0]
                shablongrdetaling()
                settingsvar.nawpage = 'receptinterwiev'
                del settingsvar.detalingname[0]
                del settingsvar.spisokGrDetailing[0]

                return render(request, settingsvar.html, context=settingsvar.nextstepdata)
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


def shablondetaling():
    iduser = funciduser()
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['detalinglist'] = settingsvar.spisoklistdetaling
    settingsvar.nextstepdata['compl'] = settingsvar.feature_name + ", " + settingsvar.detaling_feature_name
    settingsvar.nextstepdata['next'] = '  Далі '
    settingsvar.html = 'diagnoz/detaling.html'
    return


def shablongrdetaling():
    iduser = funciduser()
    if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['detalinglist'] = settingsvar.rest_apiGrDetaling
    settingsvar.nextstepdata[
        'compl'] = settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname
    settingsvar.nextstepdata['next'] = '  Далі '
    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
    settingsvar.nextstepdata['iduser'] = iduser
    settingsvar.html = 'diagnoz/grdetaling.html'

    return


def writediagnoz():

    for item in settingsvar.diagnozStroka:
        if settingsvar.kodProtokola == item['kodProtokola']:
            api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
            apiicd = rest_api('/api/DiagnozController/' + api['kodDiagnoz'] + "/0/0", '', 'GET')
            settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
            api = rest_api('/api/RecommendationController/' + api['kodRecommend'] + "/0", '', 'GET')
            settingsvar.nawpage = 'backfromcontent'
            settingsvar.html = 'diagnoz/versiyadiagnoza.html'
            iduser = funciduser()
            settingsvar.nextstepdata = {
                'opis': item['opistInterview'],
                'http': item['uriInterview'],
                'rekomendaciya': api['contentRecommendation'],
                'compl': settingsvar.nametInterview,
                'detalinglist': settingsvar.diagnozStroka,
                'iduser': iduser,
                'piblikar': ''
            }
            if len(settingsvar.pacient) > 0:
                settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                                      settingsvar.pacient['name'] + " " + settingsvar.pacient['surname']
            if len(settingsvar.likar) > 0:
                settingsvar.nextstepdata[
                    'piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
            settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
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
        settingsvar.kodProtokola = settingsvar.diagnozStroka[0]['kodProtokola']
        settingsvar.nametInterview = settingsvar.diagnozStroka[0]['nametInterview']
        writediagnoz()
    else:
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.html = 'diagnoz/errorfeature.html'
        settingsvar.nextstepdata = {}
    return


# --- Отображение на странице все параметоров установленого диагноза
def selectdiagnoz(request, select_kodProtokola, select_nametInterview):
    settingsvar.kodProtokola = select_kodProtokola
    settingsvar.nametInterview = select_nametInterview
    writediagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- повернення із перегляду змісту опитування
def backfromcontent(request):
    writediagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# --- виведення змісту інтервью
def contentinterwiev(request):  # httpRequest
    api = []
    tmp = {}
    if len(settingsvar.kodProtokola) > 0:
        api = rest_api('/api/ContentInterviewController/' + settingsvar.kodProtokola, '', 'GET')
    else:
        for item in settingsvar.spselectnameDetailing:
            tmp = {'detailsInterview': item}
            api.append(tmp)
    settingsvar.html = 'diagnoz/contentinterwiev.html'
    iduser = funciduser()
    backurl = settingsvar.nawpage
    data = {
        'compl': settingsvar.nametInterview,
        'detalinglist': api,
        'iduser': iduser,
        'backurl': backurl
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
    settingsvar.nawpage = 'receptprofillmedzaklad'
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.html = 'diagnoz/receptionprofilzaklad.html'
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'backurl': backurl,
        'compl': 'Перелік профільних медзакладів',
        'detalinglist': settingsvar.grupmedzaklad,
        'piblikar': '',
        'likar': ''
    }
    if len(settingsvar.pacient) > 0:
        settingsvar.nextstepdata['likar'] = True
        settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                              settingsvar.pacient[
                                                  'name'] + " " + settingsvar.pacient['surname']
    if len(settingsvar.likar) > 0:
        settingsvar.nextstepdata['piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
        settingsvar.nextstepdata['likar'] = True
    return


# --- вибір профільного медзакладу
def receptprofillmedzaklad(request):
    if settingsvar.kabinetitem == 'likarinterwiev':
        settingsvar.setintertview = True
        medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '', 'GET')
        settingsvar.namemedzaklad = medzaklad['name']
        settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
        settingsvar.mobtellikar = settingsvar.likar['telefon']
        saveselectlikar(settingsvar.pacient)
    else:
        selectmedzaklad('5')
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- вибір Амбулаторно-поліклінічного закладу до сімейного лікаря
def receptfamilylikar(request):
    selectmedzaklad('2')
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# --- Вибір лікаря у профільному мед закладі
def selectdprofillikar(request, selected_edrpou, selected_idstatus, selected_name):
    settingsvar.gruplikar = []
    settingsvar.namemedzaklad = selected_name
    Grupproflikar = rest_api('/api/ApiControllerDoctor/' + "0/" + selected_edrpou + "/0", '', 'GET')
    for item in Grupproflikar:
        match selected_idstatus:
            case "2":
                settingsvar.gruplikar.append(item)
            case "5":
                likarGrupDiagnoz = rest_api('/api/LikarGrupDiagnozController/' + item['kodDoctor'] + '/0', '', 'GET')
                for icdgrdiagnoz in settingsvar.grupDiagnoz:
                    for likargrdz in likarGrupDiagnoz:
                        if likargrdz['icdGrDiagnoz'] in icdgrdiagnoz['icdGrDiagnoz'] and selected_edrpou in \
                                icdgrdiagnoz[
                                    'edrpou']:
                            settingsvar.gruplikar.append(item)
                            break
                    break
    shablonlistlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def shablonlistlikar():
    settingsvar.nawpage = 'backlistlikar'
    settingsvar.html = 'diagnoz/selectedprofillikar.html'
    iduser = funciduser()
    bakurl = funcbakurl()
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': 'Перелік профільних лікарів',
        'detalinglist': settingsvar.gruplikar,
        'piblikar': '',
        'pacient': '',
        'bakurl': bakurl
    }
    if len(settingsvar.pacient) > 0:
        settingsvar.nextstepdata['likar'] = True
        settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                              settingsvar.pacient[
                                                  'name'] + " " + settingsvar.pacient['surname']
    if len(settingsvar.likar) > 0:
        settingsvar.nextstepdata['piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
        settingsvar.nextstepdata['likar'] = True

    return


# --- Поверненнф до списку лікарів
def backlistlikar(request):
    shablonlistlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# --- Функція повернення до початку опитування
def funcbakurl():
    bakurl = 'reception'
    match settingsvar.kabinet:
        case "guest":
            bakurl = 'reception'
        case "pacient":
            bakurl = 'pacient'
        case 'interwiev':
            bakurl = 'pacient'
        case 'listinterwiev':
            bakurl = 'pacient'
        case "likar":
            bakurl = 'likar'
        case 'likarinterwiev':
            bakurl = 'likar'
        case 'likarlistinterwiev':
            bakurl = 'likar'
    return bakurl


# --- Функція повернення до початку опитування
def funciduser():
    iduser = 'Анонімний відвідувач'
    match settingsvar.kabinet:
        case "guest":
            iduser = 'Анонімний відвідувач'
        case "pacient" | 'interwiev' | 'likarinterwiev':
            iduser = 'Кабінет пацієнта'
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
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
        settingsvar.html = 'diagnoz/finishinterviewpacient.html'
        settingsvar.nawpage = 'backshablonselect'
        if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev':

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
        settingsvar.likar = CmdStroka
        dateregistrationappointment(request)
    else:
        shablonselect(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- функція встановлення відповідного шаблону результатів опитування для гостя пацієнта або лікаря
def shablonselect(request):
    match settingsvar.kabinet:
        case "guest":
            settingsvar.html = 'diagnoz/pacientprofil.html'
            settingsvar.readprofil = True
            getpostpacientprofil(request)
            form = PacientForm()
            if settingsvar.html == 'diagnoz/pacientprofil.html':
                settingsvar.nextstepdata = {'form': form}
        case "pacient" | 'interwiev':
            saveselectlikar(settingsvar.pacient)

        case "likar" | 'likarinterwiev':
            saveselectlikar(settingsvar.pacient)
    return


def backshablonselect(request):
    shablonselect()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- функція вибору дати та часу прийому у лікаря
def dateregistrationappointment(request):
    visitinglist = []
    CmdStroka = rest_api('/api/VisitingDaysController/' + settingsvar.kodDoctor + "/0", '', 'GET')
    if len(CmdStroka) > 0:
        settingsvar.html = 'diagnoz/likarappointments.html'
        backurl = funcbakurl()
        iduser = funciduser()
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'likar': settingsvar.setpostlikar,
            'piblikar': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
            'complaintlist': CmdStroka,
            'backurl': backurl
        }
    else:
        shablonselect(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def selectvisitingdays(request, selected_timevizita, selected_datevizita, selected_daysoftheweek):
    settingsvar.datereception = selected_daysoftheweek + ' ' + selected_datevizita + ' ' + selected_timevizita
    shablonselect(request)
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
            'kodPacient': settingsvar.kodPacienta,
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
    saveaccount = rest_api('/api/AccountUserController/', json, 'POST')
    return
# --------------------------
# Реєстрація входу до кабінету пацієнта

def reestraccountuser(request):
    settingsvar.html = 'diagnoz/reestraccountuser.html'
    settingsvar.readprofil = False

    if request.method == 'POST':
        if settingsvar.setReestrAccount == False:
            form = ReestrAccountUserForm(request.POST)
            settingsvar.formaccount = form.data
            if len(settingsvar.formaccount['dwpassword']) == 0:
                settingsvar.setReestrAccount = False
                errorprofil('Шановний користувач! Облікові дані не корректно введені')
            else:
                if settingsvar.formaccount['password'] != settingsvar.formaccount['dwpassword']:
                    settingsvar.setReestrAccount = False
                    errorprofil('Шановний користувач! Введені паролі не співпадають')
                else:
                    json = "0/" + settingsvar.formaccount['login'] + "/" + settingsvar.formaccount['password'] + '/0'
                    Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                    if len(Stroka) > 0:
                        settingsvar.setReestrAccount = False
                        errorprofil('Шановний користувач! Обліковий запис за введеними даними вже існує')
                    else:
                        backurl = funcbakurl()
                        settingsvar.setReestrAccount = True
                        settingsvar.setpostlikar = True
                        settingsvar.html = 'diagnoz/pacientprofil.html'
                        form = PacientForm()
                        settingsvar.html == 'diagnoz/pacientprofil.html'
                        settingsvar.nextstepdata = {
                            'form': form,
                            'next': settingsvar.readprofil,
                            'backurl': backurl,
                        }
        else:
            pacientprofil(request)

    else:
        reestr = 'Реєстрація в кабінеті пацієнта'
        if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev':
            reestr = ''
        if settingsvar.setReestrAccount == False:
            settingsvar.readprofil = False
            formreestraccount = ReestrAccountUserForm()
            settingsvar.nextstepdata = {
                'form': formreestraccount,
                'backurl': 'accountuser',
                'reestrinput': reestr,
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
                settingsvar.setpost = True
                settingsvar.readprofil = True

            else:
                settingsvar.formaccount = AccountUserForm(request.POST)
                json = "0/" + settingsvar.formaccount.data['login'] + "/" + settingsvar.formaccount.data[
                    'password'] + '/0'
                Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                if len(Stroka) > 0:
                    match settingsvar.kabinetitem:
                        case "profil" | "pacient" | "interwiev" | 'listinterwiev':
                            settingsvar.kodPacienta = Stroka['idUser']
                            settingsvar.pacient = rest_api(
                                '/api/PacientController/' + settingsvar.kodPacienta + '/0/0/0/0',
                                                       '', 'GET')

                            if len(settingsvar.pacient) > 0:
                                settingsvar.setpost = True
                                settingsvar.readprofil = True
                                settingsvar.setpostlikar = True
                                formpacient = PacientForm(initial=settingsvar.pacient)
                                settingsvar.nextstepdata = {
                                'form': formpacient,
                                    'next': settingsvar.readprofil,
                                    'backurl': 'pacient'
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
                                settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
                                medzaklad = rest_api(
                                    '/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '',
                                    'GET')
                                settingsvar.namemedzaklad = medzaklad['name']
                                settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
                                settingsvar.mobtellikar = settingsvar.likar['telefon']
                                settingsvar.setpostlikar = True
                                if settingsvar.kabinetitem == 'likarinterwiev':
                                    search_pacient()
                                    settingsvar.searchaccount = True
                                else:
                                    settingsvar.setpost = True
                                    settingsvar.readprofil = True
                                    iduser = funciduser()
                                    formlikar = LikarForm(initial=settingsvar.likar)
                                    settingsvar.nextstepdata = {
                                        'form': formlikar,
                                        'next': settingsvar.readprofil,
                                        'backurl': 'likar'
                                    }
                                    settingsvar.html = 'diagnoz/likarprofil.html'
                            #                                   listlikar()
                            else:
                                errorprofil(
                                'Шановний користувач! За вказаним обліковим записом профіль лікаря не знайдено.')
                else:
                    errorprofil('Шановний користувач! Невірно введено номер телефону або пароль.')
        else:
            cab = 'Кабінет пацієнта'
            backurl = 'pacient'
            compl = 'Зареєструватися'
            if settingsvar.kabinetitem == "likar" or settingsvar.kabinetitem == 'likarinterwiev' \
                    or settingsvar.kabinetitem == 'likarlistinterwiev':
                cab = 'Кабінет лікаря'
                backurl = 'likar'
                compl = ''
            settingsvar.readprofil = False
            settingsvar.formaccount = AccountUserForm()
            settingsvar.nextstepdata = {
                'form': settingsvar.formaccount,
                'compl': compl,
                'reestrinput': cab,
                'backurl': backurl
            }
    else:
        match settingsvar.kabinetitem:
            case 'profil':
                settingsvar.readprofil = True
                iduser = funciduser()
                formpacient = PacientForm(initial=settingsvar.pacient)
                settingsvar.nextstepdata = {
                    'form': formpacient,
                    'next': settingsvar.readprofil,
                    'backurl': 'pacient'
                }
                settingsvar.html = 'diagnoz/pacientprofil.html'

            case 'interwiev':
                shablonlikar(settingsvar.pacient)

            case 'listinterwiev':
                iduser = funciduser()
                backurl = funcbakurl()
                settingsvar.html = 'diagnoz/pacientlistinterwiev.html'
                listapi = []
                listapi = rest_api('api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacienta, '', 'GET')
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
                    'next': settingsvar.readprofil,
                    'backurl': 'likar'
                }
                settingsvar.html = 'diagnoz/likarprofil.html'
            case 'likarinterwiev':
                if len(settingsvar.pacient) > 0:
                    shablonlikar(settingsvar.pacient)
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
        settingsvar.pacient = profilpacient
        settingsvar.kodPacienta = profilpacient['kodPacient']
        shablonlikar(profilpacient)
    else:
        settingsvar.search = False
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
        settingsvar.kodPacienta = "PCN." + repl[0: len(repl) - len(str(indexdia))] + str(indexdia + 1)

    return settingsvar.kodPacienta


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


def getpostpacientprofil(request):
    settingsvar.html = 'diagnoz/pacientprofil.html'
    if settingsvar.kabinetitem != 'likarinterwiev': settingsvar.kabinetitem = 'profil'
    if request.method == 'POST':
        form = PacientForm(request.POST)
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

        # --- записати в Бд облікові дані
        if settingsvar.kabinet != 'guest':
            funcaddaccount(settingsvar.formaccount.data['login'], settingsvar.formaccount.data['password'])
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
                    settingsvar.setpostlikar = True
                    errorprofil('Шановний користувач!  Ваш обліковий запис та профіль збережено.')
        else:
            errorprofil('Шановний користувач! Похибка на серевері. Ваш профіль не збережено.')
    else:
        form = PacientForm()
        settingsvar.nextstepdata = {
            'form': form,
            'next': False
        }
    return

def pacientprofil(request):  # httpRequest
    if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev':
        errorprofil('Шановний користувач! Активний кабінет пацієнта. Вхід до кабінету лікаря неможливий.')
    else:
        getpostpacientprofil()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Функція формування реквізитів профілю пацієнта для відображення на вебсайті
def shablonlikar(profilpacient):
    settingsvar.readprofil = True
    backurl = funcbakurl()
    api = rest_api('api/ApiControllerComplaint/', '', 'GET')
    settingsvar.html = 'diagnoz/receptinterwiev.html'
    shablonpacient(profilpacient)
    settingsvar.nextstepdata['complaintlist'] = api
    settingsvar.nextstepdata['backurl'] = backurl
    settingsvar.nextstepdata['likar'] = settingsvar.readprofil = True
    return


def shablonpacient(profilpacient):
    iduser = funciduser()
    backurl = funcbakurl()
    tel = ''
    mail = ''
    pind = ''
    if profilpacient['tel'] != None: tel = profilpacient['tel']
    if profilpacient['email'] != None: mail = profilpacient['email']
    if profilpacient['pind'] != None: pind = profilpacient['pind']
    tel_email_pind = 'Тел.: ' + tel + ' Ел.Пошта: ' + mail + ' Пошт.індекс: ' + pind
    settingsvar.nextstepdata = {
        'likar': settingsvar.setpostlikar,
        'iduser': iduser,
        'backurl': backurl,
        'pacient': 'Пацієнт: ' + profilpacient['profession'] + ' ' + profilpacient['name'] + " " + profilpacient[
            'surname'],
        'age_weight_growth': 'Вік: ' + str(profilpacient['age']) + 'р. Вага: ' + str(
            profilpacient['weight']) + 'кг. Зріст: ' + str(profilpacient['growth']) + 'см.',
        'tel_email_pind': tel_email_pind,
        'piblikar': '',
        'medzaklad': ''
    }
    if len(settingsvar.likar) > 0:
        settingsvar.nextstepdata['piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
        settingsvar.nextstepdata['medzaklad'] = settingsvar.namemedzaklad

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
    shablonpacient(settingsvar.pacient)
    settingsvar.nawpage = 'saveraceptionlikar'
    settingsvar.nextstepdata[
        'finishtext'] = 'Шановний користувач! Ваш протокол опитування,  попередній діагноз та запис до лікаря збережено.'
    settingsvar.html = 'diagnoz/saveraceptionlikar.html'
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Профіль пацієнта
def profilpacient(request):  # httpRequest
    cleanvars()
    settingsvar.nawpage = 'pacientprofil'
    settingsvar.kabinetitem = 'profil'
    if settingsvar.setpost == False:
        accountuser(request)
        settingsvar.initialprofil = True
    else:
        settingsvar.html = 'diagnoz/pacientprofil.html'
        if settingsvar.initialprofil == True:
            settingsvar.html = 'diagnoz/pacient.html'
            settingsvar.initialprofil = False
        else:
            settingsvar.readprofil = True
            settingsvar.initialprofil = True
            iduser = funciduser()
            formpacient = PacientForm(initial=settingsvar.pacient)
            settingsvar.nextstepdata = {
                'form': formpacient,
                'next': settingsvar.readprofil,
                'backurl': 'pacient'
            }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Провести опитування пациєнта в особистому кабінеті
def pacientinterwiev(request):  # httpRequest
    if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev':
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.kabinetitem = 'interwiev'
        settingsvar.kabinet = 'interwiev'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            shablonlikar(settingsvar.pacient)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Профіль проведеного інтервью
def profilinterview(request, selected_protokol):  # httpRequest
    if selected_protokol.find('PRT.') < 0:
        match selected_protokol:
            case 'pacient':
                settingsvar.html = 'diagnoz/pacient.html'
                settingsvar.nextstepdata = {}
            case 'pacientlistinterwiev':
                pacientlistinterwiev(request)
            case 'likar':
                settingsvar.html = 'diagnoz/likar.html'
                settingsvar.nextstepdata = {}
            case 'likarlistinterwiev':
                likarlistinterwiev(request)
            case 'interwiev' | 'listinterwiev' | 'likarinterwiev':
                funcshablonlistpacient()
    else:
        settingsvar.protokol = selected_protokol
        nextprofilinterview()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def nextprofilinterview():
    likarName = ""
    PacientName = ""
    dateint = ""
    select_dateDoctor = ""
    match settingsvar.kabinet:
        case 'listinterwiev':
            settingsvar.backurl = funcbakurl()
            funcshablonlistpacient()
        case 'likarlistinterwiev':
            listlikar()
    match settingsvar.kabinetitem:
        case "profil" | "pacient" | "interwiev" | 'listinterwiev':
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'pacientlistinterwiev'
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'likarlistinterwiev'
    settingsvar.kodProtokola = settingsvar.protokol
    iduser = funciduser()
    for item in settingsvar.listapi:
        if settingsvar.protokol == item['kodProtokola']:
            if (item['dateDoctor'] != None):
                select_dateDoctor = item['dateDoctor']
            dateint = item['dateInterview']
            match settingsvar.kabinetitem:
                case "profil" | "pacient" | "interwiev" | 'listinterwiev':
                    if item['kodDoctor'] != None and len(item['kodDoctor']) > 0:
                        doc = rest_api('api/ApiControllerDoctor/' + item['kodDoctor'] + '/0/0', '', 'GET')
                        likarName = doc['name'] + ' ' + doc['surname'] + ' Телефон: ' + doc['telefon']
                    PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']
                case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
                    if item['kodPacient'] != None and len(item['kodPacient']) > 0:
                        doc = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
                        PacientName = doc['name'] + ' ' + doc['surname'] + ' Телефон: ' + doc['tel']
                    likarName = settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
                    settingsvar.pacient = doc
            break
    depend = rest_api('api/DependencyDiagnozController/' + '0/' + settingsvar.protokol + '/0', '', 'GET')
    recommend = rest_api('api/RecommendationController/' + depend['kodRecommend'] + '/0', '', 'GET')
    diagnoz = rest_api('api/DiagnozController/' + depend['kodDiagnoz'] + '/0/0', '', 'GET')
    settingsvar.html = 'diagnoz/profilinterview.html'
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['namepacient'] = 'Пацієнт:        ' + PacientName
    settingsvar.nextstepdata['namelikar'] = 'Лікар:          ' + likarName
    settingsvar.nextstepdata['dateinterv'] = 'Дата опитування: ' + dateint
    settingsvar.nextstepdata['datereception'] = 'Дата прийому:   ' + select_dateDoctor
    settingsvar.nextstepdata['diagnoz'] = 'Попередній діагноз: ' + diagnoz['nameDiagnoza']
    settingsvar.nextstepdata['recomendaciya'] = 'Рекомендації:   ' + recommend['contentRecommendation']
    settingsvar.nextstepdata['urlinet'] = 'Опис в інтернеті:   ' + diagnoz['uriDiagnoza']
    settingsvar.nextstepdata['backurl'] = backurl

    return


def backprofilinterview(request):
    nextprofilinterview()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


#--- Перегляд проведених інтервью
# --- Функція формування шаблону для списку опитувань
def funcshablonlistpacient():
    iduser = funciduser()
    settingsvar.html = 'diagnoz/pacientlistinterwiev.html'
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['backurl'] = settingsvar.backurl
    settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacienta, '', 'GET')
    if len(settingsvar.listapi) > 0:
        settingsvar.nextstepdata['complaintlist'] = settingsvar.listapi
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return


def pacientlistinterwiev(request):  # httpRequest
    if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev':
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.backurl = funcbakurl()
        settingsvar.nawpage = 'pacientlistinterwiev'
        settingsvar.kabinet = 'listinterwiev'
        settingsvar.kabinetitem = 'listinterwiev'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            funcshablonlistpacient()
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
    if settingsvar.kabinet == 'pacient' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listinterwiev':
        errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
    else:
        cleanvars()
        settingsvar.nawpage = 'likarprofil'
        settingsvar.kabinetitem = 'likar'
        if settingsvar.setpostlikar == False:
            accountuser(request)
            settingsvar.initialprofil = True
        else:
            settingsvar.html = 'diagnoz/likarprofil.html'
            if settingsvar.initialprofil == True:
                settingsvar.html = 'diagnoz/likar.html'
                settingsvar.initialprofil = False
            else:
                settingsvar.initialprofil = True
                formlikar = LikarForm(initial=settingsvar.likar)
                settingsvar.nextstepdata = {
                    'form': formlikar,
                    'next': settingsvar.readprofil,
                    'backurl': 'likar'
                }
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
def likarinterwiev(request):  # httpRequest
    if settingsvar.kabinet == 'pacient' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listinterwiev':
        errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'likarinterwiev'
        settingsvar.kabinetitem = 'likarinterwiev'
        settingsvar.kabinet = 'likarinterwiev'
        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            # --- пошук даних пацієнта для проведення опитування
            backurl = 'likar'
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
            settingsvar.nextstepdata['backurl'] = backurl
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listlikar():
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.nawpage = 'likarlistinterweiv'
    settingsvar.html = 'diagnoz/likarlistinterwiev.html'
    settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/' + settingsvar.kodDoctor + '/0', '', 'GET')
    if len(settingsvar.listapi) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return


def likarlistinterwiev(request):  # httpRequest
    if settingsvar.kabinet == 'pacient' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listinterwiev':
        errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'profilinterview'
        settingsvar.kabinetitem = 'likarlistinterwiev'
        settingsvar.kabinet = 'likarlistinterwiev'
        if settingsvar.setpostlikar == False:
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
