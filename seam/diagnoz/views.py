import datetime
import json

import environ
import pyodbc
import requests
from django.shortcuts import render

from diagnoz import settingsvar
from .forms import PacientForm


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
    return json.loads(response.content)


#    return

def index(request):  # httpRequest
    return render(request, 'diagnoz/index.html')


def glavmeny(request):
    return render(request, 'diagnoz/glavmeny.html')

def reception(request):  # httpRequest
    return render(request, 'diagnoz/reception.html')


def pacient(request):  # httpRequest
    settingsvar.setintertview = False
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
    api = rest_api('api/ApiControllerComplaint/', '', 'GET')
    data = {
        'complaintlist': api
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
    if len(settingsvar.listfeature) <= 0:
        settingsvar.listfeature = rest_api('api/FeatureController/' + "0/" + nextfeature_keyComplaint + "/0/", '',
                                           'GET')
    html = 'diagnoz/nextfeature.html'
    data = {
        'compl': nextfeature_name,
        'next': '  Далі ',
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
                settingsvar.nextstepdata = {
                    'nextdetali': enddetaling,
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
                    'next': '  Далі ',
                    'detalinglist': settingsvar.spisoklistdetaling
                }
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
                    settingsvar.nextstepdata = {
                        'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                        'next': '  Далі ',
                        'detalinglist': settingsvar.rest_apiGrDetaling
                    }
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
        settingsvar.nextstepdata = {
            'complaintlist': rest_api('api/ApiControllerComplaint/', '', 'GET')
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
                'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
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


                data = {
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                    'next': '  Далі ',
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
            data = {
                'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name,
                'next': '  Далі ',
                'detalinglist': settingsvar.spisoklistdetaling
            }
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
                data = {
                    'compl': settingsvar.feature_name + ", " + settingsvar.detaling_feature_name + ", " + settingsvar.itemdetalingname,
                    'next': '  Далі ',
                    'detalinglist': settingsvar.rest_apiGrDetaling
                }
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
        settingsvar.diagnozStroka = rest_api('/api/InterviewController/' + "0/" + diagnozselect + "/-1/0/0", '', 'GET')
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
    api = rest_api('/api/ContentInterviewController/' + settingsvar.kodProtokola, '', 'GET')
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

    settingsvar.html = 'diagnoz/receptionprofilzaklad.html'
    settingsvar.nextstepdata = {
        'compl': 'Перелік профільних медзакладів',
        'detalinglist': settingsvar.grupmedzaklad
    }
    return


# --- вибір профільного медзакладу
def receptprofillmedzaklad(request):
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

    html = 'diagnoz/selectedprofillikar.html'
    data = {
        'compl': 'Перелік профільних лікарів',
        'detalinglist': gruplikar
    }
    return render(request, html, context=data)


# --- введення профілю пацієнта для запису на прийом до лікаря
def inputprofilpacient(request, selected_doctor):
    settingsvar.namelikar = ""
    settingsvar.mobtellikar = ""
    settingsvar.koddoctora = selected_doctor
    settingsvar.setintertview = True
    CmdStroka = rest_api('/api/ApiControllerDoctor/' + selected_doctor + "/0/0", '', 'GET')
    if len(CmdStroka) > 0:
        settingsvar.namelikar = CmdStroka['name'] + "" + CmdStroka['surname']
        settingsvar.mobtellikar = CmdStroka['telefon']
    settingsvar.html = 'diagnoz/pacientprofil.html'
    pacientprofil(request)
    form = PacientForm()
    if settingsvar.html == 'diagnoz/pacientprofil.html':
        settingsvar.nextstepdata = {'form': form}

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Зберегти протокол опитування

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


def addColectionInterview():
    details = ""
    settingsvar.dateInterview = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    settingsvar.kodComplInterv = SelectNewKodComplInteriew()
    for item in settingsvar.spisokselectDetailing:
        details = details + item + ';'
    json = {'id': 0,
            'kodDoctor': settingsvar.koddoctora,
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


def savediagnoz(request):
    # --- додати проткол опитування
    addColectionInterview()
    # ---  Додати опитування
    addCompletedInterview()
    html = 'diagnoz/savediagnoz.html'
    data = {
        'compl': 'Шановний користувач! Ваш протокол опитування та попередній діагноз збережено.',
        'backurl': 'pacient'
    }
    return render(request, html, data)


# --- кінець блоку
# ----Пациент



def receptprofillikar(request):
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
def pacientprofil(request):  # httpRequest
    settingsvar.html = 'diagnoz/pacientprofil.html'
    data = {}
    if request.method == 'POST':
        form = PacientForm(request.POST)
        #       if form.is_valid():
        json = {'id': 0,
                'KodPacient': newpacientprofil(),
                'KodKabinet': "",
                'Age': form.data['age'],
                'Weight': form.data['weight'],
                'Growth': form.data['body_height'],
                'Gender': form.data['gender'],
                'Tel': form.data['mob_telefon'],
                'Email': form.data['email'],
                'Name': form.data['firstName'],
                'Surname': form.data['lastName'],
                'Pind': form.data['post_index'],
                'Profession': form.data['profession']
                }

        # --- записати в Бд введенний профіль
        saveprofil = rest_api('/api/PacientController/', json, 'POST')
        if len(saveprofil) > 0:
            if settingsvar.setintertview == True:
                settingsvar.html = 'diagnoz/finishreception.html'
                settingsvar.nextstepdata = {
                    'pacient': json['Name'] + " " + json['Surname'],
                    'shapka': 'Увага! Ви сформували запит на прийом до лікаря.',
                    'medzaklad': settingsvar.namemedzaklad,
                    'likar': 'Лікар: ' + settingsvar.namelikar + "тел.: " + settingsvar.mobtellikar,
                    'datereception': 'Дата прийому: ' + settingsvar.datereception,
                    'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
                    'podval': 'Ви підтверджуєте свій вибір?'
                }
            else:
                settingsvar.html = 'diagnoz/savediagnoz.html'
                settingsvar.nextstepdata = {
                    'compl': 'Шановний користувач! Ваш профіль збережено.',
                    'backurl': 'pacient'
                }
        else:
            settingsvar.html = 'diagnoz/savediagnoz.html'
            settingsvar.nextstepdata = {
                'compl': 'Шановний користувач! Похибка на серевері. Ваш профіль не збережено.',
                'backurl': 'pacient'
            }

    #        return render(request, settingsvar.html,settingsvar.nextstepdata )

    else:
        form = PacientForm()
        settingsvar.nextstepdata = {'form': form}
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---  Збереження запису до лікаря в історії пацієнта
def addReceptionPacient():
    json = {'id': 0,
            'KodPacient': settingsvar.kodPacient,
            'KodDoctor': settingsvar.koddoctora,
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
            'KodPacient': settingsvar.kodPacient,
            'KodDoctor': settingsvar.koddoctora,
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
    settingsvar.nextstepdata = {
        'finishtext': 'Шановний користувач! Ваш протокол опитування,  попередній діагноз та запис до лікаря збережено.'
    }
    settingsvar.html = 'diagnoz/saveraceptionlikar.html'
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

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
