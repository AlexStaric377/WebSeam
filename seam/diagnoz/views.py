import datetime
import json
from datetime import datetime, timedelta

# from selenium.webdriver.common.keys import Keys
import environ
import pyodbc
import requests
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.shortcuts import render

from diagnoz import settingsvar
from .forms import (PacientForm, AccountUserForm, ReestrAccountUserForm,
                    SearchPacient, LikarForm, Reestrvisitngdays, ReestrPulsTiskForm,
                    InputsearchcomplateForm, InputsearchpacientForm)

# from selenium import webdriver
# from IPython.display import Javascript

'''

view-функция, которая будет и отображать страницу (GET-запрос), 
и обрабатывать попытку входа (POST-запрос). Django предоставляет готовую форму AuthenticationForm.


'''


def home_view(request):  # Или любое другое ваше view
    # Инициализируем форму регистрации логина и пароля для входа в кабинет
    settingsvar.html = 'diagnoz/index.html'
    settingsvar.backpage = 'home_view'
    loginuser(request)

    return render(request, settingsvar.html, settingsvar.nextstepdata)


def loginuser(request):
    # Инициализируем форму регистрации логина и пароля для входа в кабинет
    if request.method == 'POST':
        # Если форма отправлена, обрабатываем данные
        login_form = AuthenticationForm(request, data=request.POST)
        settingsvar.formsearch = login_form.data
        if len(settingsvar.formsearch['username']) > 0:
            numbtel = settingsvar.formsearch['username'][1:]
            if numbtel.isnumeric():
                if len(numbtel) == 12:
                    json = "0/" + settingsvar.formsearch['username'] + "/" + settingsvar.formsearch['password'] + '/0'
                    Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                    if 'idStatus' in Stroka:
                        request.method = 'GET'
                        login_form = AuthenticationForm()
                        match Stroka['idStatus']:
                            case '1':  # 1- адміністратор,
                                settingsvar.setpost = True
                            case '2':  # 2- пацієнт,
                                settingsvar.kodPacienta = Stroka['idUser']
                                settingsvar.pacient = rest_api(
                                    '/api/PacientController/' + settingsvar.kodPacienta + '/0/0/0/0', '', 'GET')
                                if len(settingsvar.pacient) > 0:
                                    settingsvar.setpost = True
                                    settingsvar.readprofil = True
                                    settingsvar.setpostlikar = True
                                    settingsvar.kabinet = settingsvar.backpage = 'pacient'
                                    settingsvar.html = 'diagnoz/pacient.html'

                            case '3' | '4' | '5':  # 3- лікар, 4 - лікар адміністратор, 5- резерв

                                settingsvar.kodLikar = Stroka['idUser']
                                settingsvar.likar = rest_api(
                                    '/api/ApiControllerDoctor/' + settingsvar.kodLikar + '/0/0',
                                    '', 'GET')
                                if 'kodDoctor' in settingsvar.likar:
                                    settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
                                    medzaklad = rest_api(
                                        '/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0',
                                        '',
                                        'GET')
                                    settingsvar.namemedzaklad = medzaklad['name']
                                    settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar[
                                        'surname']
                                    settingsvar.mobtellikar = settingsvar.likar['telefon']
                                    settingsvar.statuslikar = medzaklad['idStatus']
                                    settingsvar.setpost = True
                                    settingsvar.readprofil = True
                                    settingsvar.setpostlikar = True
                                    settingsvar.initialprofil = True
                                    settingsvar.kabinet = settingsvar.backpage = 'likar'
                                    settingsvar.html = 'diagnoz/likar.html'
                    else:
                        messages.error(request, 'Неверное имя пользователя или пароль.')
                else:
                    errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
            else:
                errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
        else:
            errorprofil("Шановний користувач!  Не введено номер телефону.")

    #        else:
    # Если форма невалидна (неверный пароль/логин),
    # мы НЕ перенаправляем, а просто даем странице
    # отрендериться снова с этой же формой (в ней уже будут ошибки)
    #            messages.error(request, 'Неверное имя пользователя или пароль.')

    # user = authenticate(username=username, password=password)
    #            if username == "admin":
    #                context = {
    #                }
    #                return render(request, 'diagnoz/likar.html', context)

    #            if user is not None:
    # Входим в систему
    #                login(request, user)
    #                messages.success(request, f'Добро пожаловать, {username}!')
    #                return redirect('/')  # Перенаправляем на главную (или куда нужно)
    #            else:
    #                return render(request, 'diagnoz/likar.html', context)
    #        else:
    # Если форма невалидна (неверный пароль/логин),
    # мы НЕ перенаправляем, а просто даем странице
    # отрендериться снова с этой же формой (в ней уже будут ошибки)
    #            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        login_form = AuthenticationForm()
        # ----- Добавляем класс 'form-control' для полей -----
        # Это простой способ добавить Bootstrap-стили без crispy-forms
        login_form.fields['username'].widget.attrs.update({'class': 'form-control'})
        login_form.fields['password'].widget.attrs.update({'class': 'form-control'})
        # ---------------------------------------------------
        if settingsvar.kabinet != '': exitkab()
    settingsvar.nextstepdata = {'login_form': login_form}

    return


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
            response = requests.put(urls, headers=headers, data=json.dumps(data))
        case 'DEL':
            response = requests.delete(urls)
    stroka = []
    if len(response.content) > 1:
        stroka = json.loads(response.content)

    return stroka


# def backindex(request):  # httpRequest
#    login()
#    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def index(request):  # httpRequest
    settingsvar.html = 'diagnoz/index.html'
    settingsvar.kabinet = 'index'
    loginuser(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def reception(request):  # httpRequest

    json = ('IdUser: guest,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: reception')
    unloadlog(json)
    backreception()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backreception():
    settingsvar.backpage = 'index'
    settingsvar.receptitem = ""
    settingsvar.kabinet = 'guest'
    settingsvar.likar = {}
    settingsvar.pacient = {}
    settingsvar.setintertview = False
    settingsvar.kabinetitem = 'guest'
    settingsvar.interviewcompl = False
    settingsvar.setpost = False
    settingsvar.search = False
    settingsvar.zgodayes = False
    settingsvar.datereception = 'призначається за тел.'
    settingsvar.datedoctor = 'призначається за тел.'
    settingsvar.html = 'diagnoz/reception.html'
    settingsvar.funciya = ''
    settingsvar.icdGrDiagnoz = ''
    return


def pacient(request):  # httpRequest
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev') and len(
        settingsvar.likar) > 0:
        errorprofil('Шановний користувач! Активний кабінет пацієнта. Вхід до кабінету лікаря неможливий.')
    else:
        funcpacient()
        if request.method == 'POST':
            loginuser(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funcpacient():
    json = ('IdUser: pacient,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pacient')
    unloadlog(json)
    settingsvar.backpage = 'index'
    settingsvar.kabinet = 'pacient'
    settingsvar.setintertview = False
    settingsvar.interviewcompl = False
    settingsvar.zgodayes = False
    settingsvar.formpacient = ""
    settingsvar.html = 'diagnoz/pacient.html'

    settingsvar.likar = {}
    settingsvar.datereception = 'призначається за тел.'
    settingsvar.datedoctor = 'призначається за тел.'
    settingsvar.funciya = ''
    return


# --- Вийти з кабінету
def exitkab():
    cleanvars()
    settingsvar.setpostlikar = False
    settingsvar.setpost = False
    settingsvar.likar = {}
    settingsvar.pacient = {}
    settingsvar.kabinet = {}
    settingsvar.formsearch = {}
    settingsvar.funciya = ''
    return


def exitkabinet(request):  #
    exitkab()
    settingsvar.html = 'diagnoz/index.html'
    loginuser(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def likar(request):  # httpRequest
    if ((
            settingsvar.kabinet == 'pacient' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listinterwiev')
            and len(settingsvar.pacient) > 0):
        errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
    else:
        json = ('IdUser: likar,' + 'dateseanse :' +
                datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likar')
        unloadlog(json)
        settingsvar.backpage = 'index'
        settingsvar.receptitem = 'index'
        settingsvar.kabinet = 'likar'
        settingsvar.html = 'diagnoz/likar.html'
        settingsvar.setintertview = False
        settingsvar.search = False
        settingsvar.interviewcompl = False
        settingsvar.ongrupdetaling = False

        settingsvar.pacient = {}
        settingsvar.datereception = 'призначається за тел:'
        settingsvar.datedoctor = 'не встановлено'
        settingsvar.funciya = ''
        settingsvar.nextstepdata = {
            'mainbar': True}
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def testnav(request):  # httpRequest
    return render(request, 'diagnoz/testnav.html')

def setings(request):  # httpRequest
    return render(request, 'diagnoz/setings.html')


def proseam(request):
    json = ('IdUser: proseam,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: proseam')
    unloadlog(json)
    settingsvar.backpage = 'index'
    return render(request, 'diagnoz/proseam.html')


def rada(request):
    json = ('IdUser: rada,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: rada')
    unloadlog(json)
    settingsvar.backpage = 'index'
    return render(request, 'diagnoz/rada.html')


def pronas(request):
    json = ('IdUser: pronas,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pronas')
    unloadlog(json)
    return render(request, 'diagnoz/pronas.html')


def newsseam(request):
    json = ('IdUser: newsseam,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: newsseam')
    unloadlog(json)
    return render(request, 'diagnoz/newsseam.html')


def applicregulat(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'applicregulat'
    json = ('IdUser: applicregulat,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: applicregulat')
    unloadlog(json)
    return render(request, 'diagnoz/applicregulat.html')


def manuallikar(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'manuallikar'
    json = ('IdUser: manuallikar,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: manuallikar')
    unloadlog(json)
    return render(request, 'diagnoz/manuallikar.html')


def manualpacient(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'manualpacient'
    json = ('IdUser: manualpacient,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: manualpacient')
    unloadlog(json)
    return render(request, 'diagnoz/manualpacient.html')


def manualseam(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'manualseam'
    json = ('IdUser: manualpacient,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: manualseam')
    unloadlog(json)
    return render(request, 'diagnoz/manualseam.html')

# ---- Реєстрація профілю пацієнта
def registrprofil(request):
    settingsvar.backpage = settingsvar.kabinet
    if settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'likarinterwiev':
        shablonlikar(request, settingsvar.pacient)
    else:
        iduser = funciduser()
        backurl = funcbakurl()
        settingsvar.receptitem = 'registrprofil'
        if request.method == 'POST':
            pacientprofil(request)
        else:
            settingsvar.html = 'diagnoz/pacientprofil.html'
            form = PacientForm()
            settingsvar.nextstepdata = {
                'form': form,
                'next': settingsvar.readprofil,
                'backurl': backurl,
                'iduser': iduser
            }

    json = ('IdUser: registrprofil,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: registrprofil')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---- Реєстрація кабінету пацієнта
def registrkabinet(request):
    if settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'likarinterwiev':
        settingsvar.backpage = settingsvar.kabinet
        shablonlikar(request, settingsvar.pacient)
    else:
        settingsvar.backpage = settingsvar.kabinet
        settingsvar.receptitem = 'registrkabinet'
        reestraccountuser(request)
    json = ('IdUser: registrkabinet' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: registrkabinet')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---- Профільні лікарі
def profillikar(request):
    if settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'likarinterwiev':
        settingsvar.backpage = settingsvar.kabinet
        shablonlikar(request, settingsvar.pacient)
    else:
        settingsvar.backpage = settingsvar.kabinet
        settingsvar.receptitem = 'profillikar'
        likarspec = []

        settingsvar.likar = rest_api('/api/ApiControllerDoctor/', '', 'GET')
        for item in settingsvar.likar:
            medzaklad = rest_api(
                '/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '',
                'GET')
            if medzaklad['idStatus'] == '5':
                likarspec.append(item)
        if len(likarspec) > 0:
            selectlikarrofil(likarspec)
        else:
            errorprofil('Шановний користувач! за вашим запитом немає спецілізованих лікарів')
    json = ('IdUser: profillikar' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: profillikar')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def replaceproflikar(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'replaceproflikar'
    settingsvar.html = 'diagnoz/selectlikarprofil.html'
    settingsvar.nextstepdata = {}
    tmplikar = {}
    likarspec = []
    diagnoz = rest_api('api/DiagnozController/' + settingsvar.kodDiagnoz + '/0/0', '', 'GET')

    settingsvar.likar = rest_api('/api/LikarGrupDiagnozController/' + '0/' + diagnoz['icdGrDiagnoz'], '', 'GET')
    for item in settingsvar.likar:
        itemlikar = rest_api('api/ApiControllerDoctor/' + item['kodDoctor'] + '/0/0', '', 'GET')

        tmplikar['kodDoctor'] = itemlikar['kodDoctor']
        tmplikar['kodzaklad'] = itemlikar['edrpou']
        tmplikar['icdGrDiagnoz'] = diagnoz['icdGrDiagnoz']
        tmplikar['name'] = itemlikar['name']
        tmplikar['surname'] = itemlikar['surname']
        tmplikar['specialnoct'] = itemlikar['specialnoct']
        zaklad = rest_api('api/MedicalInstitutionController/' + itemlikar['edrpou'] + '/0/0/0', '', 'GET')
        tmplikar['namezaklad'] = zaklad['name']
        tmplikar['zakladname'] = zaklad['name']
        tmplikar['adreszak'] = zaklad['adres']
        tmplikar['tel'] = zaklad['telefon']
        likarspec.append(tmplikar)
        tmplikar = {}
    if len(likarspec) > 0:

        iduser = funciduser()
        backurl = funcbakurl()
        familylikar = workdirection = True
        likar = False

        compl = 'Перелік спеціалізованих лікарів'
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'compl': compl,
            'detalinglist': likarspec,
            'piblikar': '',
            'pacient': '',
            'likar': likar,
            'backurl': backurl,
            'workdirection': workdirection,
            'familylikar': familylikar,
            'namediagnoz': diagnoz['icdGrDiagnoz']
        }
        if len(settingsvar.pacient) > 0:
            # settingsvar.nextstepdata['likar'] = True
            settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                                  settingsvar.pacient['name'] + " " + settingsvar.pacient['surname']

    else:
        errorprofil('Шановний користувач! за вашим запитом немає спецілізованих лікарів')

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)



# ---- Амбулаторно-поліклінічні заклади
def clinicmedzaklad(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'clinicmedzaklad'
    statuszaklad = '2'
    selectmedzaklad(request, statuszaklad)

    json = ('IdUser: clinicmedzaklad' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: clinicmedzaklad')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---- Сімейні лікарі
def familylikar(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'familylikar'
    likarspec = []

    settingsvar.likar = rest_api('/api/ApiControllerDoctor/', '', 'GET')
    for item in settingsvar.likar:
        medzaklad = rest_api(
                '/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '',
                'GET')
        if medzaklad['idStatus'] == '2':
                likarspec.append(item)
    if len(likarspec) > 0:
        selectlikarrofil(likarspec)
    else:
        errorprofil('Шановний користувач! за вашим запитом немає сімейних лікарів')

    json = ('IdUser: familylikar' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: familylikar')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Дії при першій допомозі людині що нездужає
def ambulance(request):
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.receptitem = 'ambulance'
    settingsvar.html = 'diagnoz/ambulance.html'
    json = ('IdUser: ambulance' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: ambulance')
    unloadlog(json)
    return render(request, settingsvar.html)


# Дії при першій допомозі Головний біль.
def headache(request):
    settingsvar.procedura = settingsvar.receptitem = 'headache'
    settingsvar.search_reason = 'Перша+домедична+допомога+біль+в+голові'
    homemedicalcare()
    return render(request, 'diagnoz/headache.html', settingsvar.nextstepdata)


# Перші дії в допомозі при кровотечі.
def krovotecha(request):
    settingsvar.procedura = settingsvar.receptitem = 'krovotecha'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+кровотечі'
    homemedicalcare()
    return render(request, 'diagnoz/krovotecha.html', settingsvar.nextstepdata)


# ---  Oпік
def singe(request):
    settingsvar.procedura = settingsvar.receptitem = 'singe'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+опіку'
    homemedicalcare()
    return render(request, 'diagnoz/singe.html', settingsvar.nextstepdata)


# ---  Хімічий опік
def chemicalburn(request):
    settingsvar.procedura = settingsvar.receptitem = 'chemicalburn'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+хімічному+опіку'
    homemedicalcare()
    return render(request, 'diagnoz/chemicalburn.html', settingsvar.nextstepdata)


# --- Біль у голрі

def sorethroat(request):
    settingsvar.procedura = settingsvar.receptitem = 'sorethroat'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+болю+у+горлі'
    homemedicalcare()
    return render(request, 'diagnoz/sorethroat.html', settingsvar.nextstepdata)


# --- Біль у серці
def heartache(request):
    settingsvar.procedura = settingsvar.receptitem = 'heartache'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+болю+у+серці'
    homemedicalcare()
    return render(request, 'diagnoz/heartache.html', settingsvar.nextstepdata)


# --- Біль у животі
def abdominalpain(request):
    settingsvar.procedura = settingsvar.receptitem = 'abdominalpain'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+болю+у+животі'
    homemedicalcare()
    return render(request, 'diagnoz/abdominalpain.html', settingsvar.nextstepdata)


# --- Біль у вухах
def earache(request):
    settingsvar.procedura = settingsvar.receptitem = 'earache'
    settingsvar.search_reason = 'Перша+домедична+допомога+при+болю+у+вухах'
    homemedicalcare()
    return render(request, 'diagnoz/earache.html', settingsvar.nextstepdata)


# --- процедура формування шаблону сторінки
def homemedicalcare():
    settingsvar.backpage = settingsvar.kabinet
    reason_url = reason_url = 'https://www.google.com/search'
    settingsvar.nextstepdata = {
        'reason_url': reason_url,
        'search_reason': settingsvar.search_reason,
    }
    json = ('IdUser: ' + settingsvar.procedura + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura:' + settingsvar.procedura)
    unloadlog(json)
    return


# напрямки проведення діагностики в системі
def directiondiagnoz(request):
    json = ('IdUser: directiondiagnoz,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: directiondiagnoz')
    unloadlog(json)
    settingsvar.directdiagnoz = True
    settingsvar.kabinet = 'guest'
    settingsvar.backpage = 'guest'
    settingsvar.receptitem = 'directiondiagnoz'
    listworkdiagnoz()
    settingsvar.nextstepdata['piblikar'] = ""
    settingsvar.nextstepdata['medzaklad'] = ""

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def unloadlog(json):
    Stroka = rest_api('api/UnloadController/' + "loguser/" + json + "/0", '', 'GET')
    return


# --- Блок Опитування і встановлення діагнозу
# --- 1. Де або яке нездужання


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
    settingsvar.zgodayes = False
    settingsvar.ongrupdetaling = False
    settingsvar.DiagnozRecomendaciya = []
    settingsvar.rest_apisetdiagnoz = ""
    settingsvar.spisokkeyinterview = []
    settingsvar.spisoknameinterview = []
    settingsvar.strokagrdetaling = ""
    settingsvar.diagnozStroka = []
    settingsvar.kodProtokola = ""
    settingsvar.setintertview = False
    settingsvar.interviewcompl = False
    settingsvar.nextstepdata = {}
    settingsvar.searchaccount = False
    return


def interwievcomplaint(request):
    if settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'likarinterwiev':
        settingsvar.backpage = settingsvar.kabinet
        shablonlikar(request, settingsvar.pacient)
    else:
        cleanvars()
        settingsvar.directdiagnoz = False
        settingsvar.receptitem = 'interwievcomplaint'

        match settingsvar.kabinet:
            case 'guest':
                settingsvar.setpostlikar = False
                settingsvar.interviewcompl = True
                settingsvar.backpage = 'interwievcomplaint'

            case 'pacient' | 'interwiev' | 'likar' | 'likarinterwiev':
                settingsvar.setpostlikar = True
        funcinterwiev(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funcinterwiev(request):
    settingsvar.complate = 'funcsearchcomplate'
    iduser = funciduser()
    settingsvar.kodDoctor = ""
    # settingsvar.pacient = {}
    settingsvar.DiagnozRecomendaciya = []
    settingsvar.spisokkeyinterview = []
    settingsvar.spisokkeyfeature = []
    settingsvar.spisokselectDetailing = []
    settingsvar.spisoklistdetaling = []
    settingsvar.spisokGrDetailing = []
    settingsvar.сomplaintselect = []
    settingsvar.strokagrdetaling = ""
    settingsvar.ongrupdetaling = False
    settingsvar.selectfeature = False
    settingsvar.viewdetaling = False
    funsearchcomplform(request)
    match settingsvar.kabinet:
        case 'guest':
            settingsvar.pacient = {}
            if settingsvar.receptitem == 'InputsearchcomplateForm':
                if settingsvar.backpage == 'interwievcomplaint':
                        settingsvar.backpage = 'reception'
                else:
                        settingsvar.backpage = 'interwievcomplaint'

        case 'pacientinterwiev':
            settingsvar.receptitem = 'pacient'
        case 'interwiev':
            if settingsvar.receptitem != 'getsearchcomplateForm' and settingsvar.selectbackmeny != True:
                settingsvar.receptitem = 'pacientinterwiev'

        case 'likar':

            if settingsvar.receptitem == 'getsearchcomplateForm':
                if settingsvar.backpage == 'likarinterwiev': settingsvar.backpage = 'likar'
            else:
                if settingsvar.receptitem == 'InputsearchcomplateForm':
                    if settingsvar.backpage == 'likarinterwiev':
                        settingsvar.backpage = 'likar'
                    else:
                        settingsvar.backpage = 'likarinterwiev'
                else:
                    settingsvar.backpage = 'likar'
    pacient = " "
    likar = False
    if len(settingsvar.pacient) > 0:
        pacient = settingsvar.pacient['profession'] + "  " + settingsvar.pacient['name'] + " " + settingsvar.pacient[
            'surname']
        likar = True
    settingsvar.nawpage = 'receptinterwiev'
    settingsvar.html = 'diagnoz/receptinterwiev.html'
    settingsvar.nextstepdata = {
        'complaintlist': settingsvar.сomplaintselect,
        'iduser': iduser,
        'likar': likar,
        'backurl': 'reception',
        'backpage': settingsvar.backpage,
        'complsearh': settingsvar.complate,
        'pacient': 'Пацієнт: ' + pacient,
        'form': settingsvar.formsearchtext
    }
    return


def funsearchcomplform(request):
    if request.method == 'POST':
        form = InputsearchcomplateForm(request.POST)
        settingsvar.searchtext = form.data
        tmp = []
        settingsvar.receptitem = 'InputsearchcomplateForm'
        complate = settingsvar.searchtext['searchcomplate'].rstrip()
        for item in settingsvar.apiсomplaint:
            if complate.upper() in item['name'].upper():
                tmp.append(item)
        settingsvar.сomplaintselect = tmp
        request.method = 'GET'
        settingsvar.formsearchtext = InputsearchcomplateForm(initial=settingsvar.searchtext)
    else:
        if settingsvar.receptitem == 'getsearchcomplateForm':

            settingsvar.receptitem = 'likar'

            settingsvar.selectbackmeny = False
        else:
            settingsvar.receptitem = 'getsearchcomplateForm'
        settingsvar.apiсomplaint = rest_api('api/ApiControllerComplaint/', '', 'GET')
        settingsvar.сomplaintselect = settingsvar.apiсomplaint
        settingsvar.formsearchtext = InputsearchcomplateForm()

    return


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
    settingsvar.dictfeature = []
    settingsvar.keyComplaint = nextfeature_keyComplaint
    if len(settingsvar.listfeature) <= 0:
        settingsvar.listfeature = rest_api('api/FeatureController/' + "0/"
                                           + nextfeature_keyComplaint + "/0/", '', 'GET')
        tmp = []
        for item in settingsvar.listfeature:

            item['checkfeat'] = False
            item['checkfeature'] = False
            tmp.append(item)
        settingsvar.listfeature = tmp
        # for item in settingsvar.listfeature:
        #     listkeyFeature = settingsvar.keyComplaint + ";" + item['keyFeature'] + ";"
        #     dictfeature = rest_api('api/InterviewController/' + "0/0/0/0/" + listkeyFeature, '', 'GET')
        #     if len(dictfeature) > 0:
        #         for itemfeature in dictfeature:
        #             if item['keyFeature'] in itemfeature['grDetail']:
        #                 settingsvar.selectfeature = True
        #                 settingsvar.spisoknamefeature.append(item['name'])
        #                 settingsvar.spselectnameDetailing.append(item['name'])
        # funcselectfeature()
    iduser = funciduser()
    settingsvar.nawpage = 'backfeature'
    settingsvar.html = 'diagnoz/nextfeature.html'

    if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['featurelist'] = settingsvar.listfeature
    settingsvar.nextstepdata['next'] = '  Далі '
    settingsvar.nextstepdata['compl'] = settingsvar.feature_name
    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
    settingsvar.nextstepdata['iduser'] = iduser
    settingsvar.nextstepdata['selectfeature'] = settingsvar.selectfeature

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Вибір харектеру прояву. Одинокий чи груповий (чиханння, соплі, свербіння)
def funcselectfeature():
    settingsvar.selectfeature = False
    tmplist = []
    index = settingsvar.indexfeature = 0
    settingsvar.html = 'diagnoz/errorfeature.html'
    if len(settingsvar.dictfeature) == 0:
        listkeyFeature = settingsvar.keyComplaint + ";" + settingsvar.keyFeature + ";"
        settingsvar.dictfeature = rest_api('api/InterviewController/' + "0/0/0/0/" + listkeyFeature, '', 'GET')

    if len(settingsvar.dictfeature) > 0:
        if len(settingsvar.keyFeature) != 0:
            for item in settingsvar.listfeature:
                if item['keyFeature'] == settingsvar.keyFeature and item['keyComplaint'] == settingsvar.keyComplaint:
                    item['checkfeature'] = True
                    break
            for item in settingsvar.listfeature:
                for itemfeature in settingsvar.dictfeature:
                    if item['keyFeature'] in itemfeature['grDetail']:
                        if settingsvar.keyFeature == item['keyFeature']:
                            settingsvar.indexfeature = index
                            settingsvar.spisoknamefeature.append(item['name'])
                            settingsvar.spselectnameDetailing.append(item['name'])
                        index = index + 1
                        settingsvar.selectfeature = True
                        break
                for itemfeature in settingsvar.dictfeature:
                    if item['keyFeature'] in itemfeature['grDetail']:
                        if item not in tmplist:
                            tmplist.append(item)
            settingsvar.listfeature = tmplist
    else:
        cleanvars()
        iduser = funciduser()
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.html = 'diagnoz/receptinterwiev.html'
        api = rest_api('api/ApiControllerComplaint/', '', 'GET')
        settingsvar.nextstepdata = {
            'complaintlist': api,
            'iduser': iduser,
            'backurl': 'reception'
        }
    return


# --- Формування масиву обраних симптомів групових деталей характеру прояву знедужання
def detaling_checkbox_view(request, select_detaling):
    tmp = []
    if request.method == 'POST':

        # time.sleep(1)
        # tmp = request.body
        # string_data = tmp.decode('utf-8')
        # if '{' in string_data:
        #     data = eval(string_data)
        # Если флажок включен, вернется 'True', иначе False
        data = json.loads(request.body)
        activ_checkbox = data['active']

        for item in settingsvar.spisoklistdetaling:
            if item['kodDetailing'] == select_detaling:
                if activ_checkbox == True: item['checkfeat'] = True
                if activ_checkbox == False: item['checkfeat'] = False
            else:
                if 'checkfeat' not in item:
                    item['checkfeat'] = False
            tmp.append(item)
        settingsvar.spisoklistdetaling = []
        for item in tmp:
            settingsvar.spisoklistdetaling.append(item)
        request.method = 'GET'
    settingsvar.nextstepdata['detalinglist'] = settingsvar.spisoklistdetaling

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Формування масиву обраних симптомів групових деталей характеру прояву знедужання
def grdetaling_checkbox_view(request, select_grdetaling):
    tmp = []
    if request.method == 'POST':
        data = json.loads(request.body)
        activ_checkbox = data['active']

        for item in settingsvar.rest_apiGrDetaling:
            if item['kodDetailing'] == select_grdetaling:
                if activ_checkbox == True: item['checkfeat'] = True
                if activ_checkbox == False: item['checkfeat'] = False
            else:
                if 'checkfeat' not in item:
                    item['checkfeat'] = False
            tmp.append(item)
        settingsvar.rest_apiGrDetaling = []
        for item in tmp:
            settingsvar.rest_apiGrDetaling.append(item)
        request.method = 'GET'
    settingsvar.nextstepdata['detalinglist'] = settingsvar.rest_apiGrDetaling

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)




# Характер прояву нездужання
def featurespisok(request, featurespisok_keyComplaint, featurespisok_keyFeature):
    settingsvar.DiagnozRecomendaciya.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyinterview.append(featurespisok_keyFeature + ";")
    settingsvar.spisokkeyfeature.append(featurespisok_keyFeature)
    settingsvar.spisokselectDetailing.append(featurespisok_keyFeature)
    settingsvar.keyFeature = featurespisok_keyFeature
    settingsvar.keyComplaint = featurespisok_keyComplaint
    funcfeature(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backfeature(request):
    funcfeature(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funcfeature(request):
    if len(settingsvar.spisoklistdetaling) == 0:
        if len(settingsvar.spisokGrDetailing) == 0 and settingsvar.ongrupdetaling == False:
            iduser = funciduser()
            settingsvar.nextstepdata = {}
            settingsvar.itemstep = 'spisokkeyfeature'
            settingsvar.nawpage = 'backfeature'
            settingsvar.forspisokkeyfeature = False
            funcselectfeature()
            if len(settingsvar.listfeature) > 1:
                settingsvar.html = 'diagnoz/nextfeature.html'
                if settingsvar.selectfeature == False:
                    del settingsvar.listfeature[settingsvar.indexfeature]

                if len(settingsvar.pacient) > 0:
                    shablonpacient(settingsvar.pacient)
                settingsvar.nextstepdata['featurelist'] = settingsvar.listfeature
                settingsvar.nextstepdata['next'] = '  Далі '
                settingsvar.nextstepdata['compl'] = settingsvar.feature_name
                settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
                settingsvar.nextstepdata['iduser'] = iduser
                settingsvar.nextstepdata['selectfeature'] = settingsvar.selectfeature

            if len(settingsvar.listfeature) == 1:
                nextstepgrdetaling()
        else:
            return redirect(request.path)
    else:
        return redirect(request.path)
    return


def feature_checkbox_view(request, select_keyComplaint, select_keyFeature):
    tmp = []
    if request.method == 'POST':

        data = json.loads(request.body)
        activ_checkbox = data['active']

        for item in settingsvar.listfeature:
            if item['keyFeature'] == select_keyFeature and item['keyComplaint'] == select_keyComplaint:
                if activ_checkbox == True: item['checkfeature'] = True
                if activ_checkbox == False: item['checkfeature'] = False
            else:
                if 'checkfeature' not in item:
                    item['checkfeature'] = False
            tmp.append(item)

        settingsvar.listfeature = []
        for item in tmp:
            settingsvar.listfeature.append(item)

        request.method = 'GET'
    settingsvar.nextstepdata['featurelist'] = settingsvar.listfeature

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---- чистка переменніх перед поавторным началом диагностика
def claenvarfuture():
    settingsvar.listfeature = []
    settingsvar.DiagnozRecomendaciya = []
    settingsvar.spisokkeyinterview = []
    settingsvar.spisokkeyfeature = []
    settingsvar.spisokselectDetailing = []
    settingsvar.ongrupdetaling = False
    settingsvar.viewdetaling = False
    settingsvar.keyFeature = {}
    settingsvar.keyComplaint = {}
    settingsvar.itemstep = ""
    return


# --- 3. Деталізація характеру нездужання

def nextgrdetaling(request):
    if len(settingsvar.spisoklistdetaling) == 0 and len(settingsvar.spisokGrDetailing) == 0:
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
    else:
        return redirect(request.path)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Блок поиска и вывода описания диагноза

# --- функция распределения списков симптомов по локальным и групповым
def nextstepgrdetaling():
    if settingsvar.itemstep == 'spisokkeyfeature' or settingsvar.itemstep == "":
        settingsvar.viewdetaling = False
        settingsvar.continuegrdetaling = False
        settingsvar.detalingname = []
        settingsvar.listdetaling = {}
        settingsvar.spisokGrDetailing = []
        settingsvar.spisoklistdetaling = []

        for item in settingsvar.listfeature:
            if item['checkfeature'] == True:
                if item['keyFeature'] not in settingsvar.spisokkeyfeature:
                    settingsvar.spisokkeyfeature.append(item['keyFeature'])

        if len(settingsvar.spisokkeyfeature) > 0:
            for keyfeature in settingsvar.spisokkeyfeature:
                listkeyfeature = rest_api('api/DetailingController/' + "0/" + keyfeature + "/0/", '', 'GET')
                for itemkeyfeature in listkeyfeature:
                    set = ""
                    settingsvar.itemstep = 'spisoklist'
                    if itemkeyfeature['keyGrDetailing'] != None:
                        if itemkeyfeature['keyGrDetailing'] == "":
                            settingsvar.spisoklistdetaling.append(itemkeyfeature)
                            if itemkeyfeature['keyFeature'] not in settingsvar.strokagrdetaling:
                                settingsvar.strokagrdetaling = (settingsvar.strokagrdetaling +
                                                                itemkeyfeature['keyFeature'] + ";")
                        else:
                            if len(itemkeyfeature['keyGrDetailing']) > 5:
                                # settingsvar.detalingname.append(itemkeyfeature['nameDetailing'])
                                if itemkeyfeature['keyFeature'] in settingsvar.strokagrdetaling:
                                    if itemkeyfeature['keyGrDetailing'] not in settingsvar.strokagrdetaling:
                                        set = settingsvar.strokagrdetaling + itemkeyfeature['keyGrDetailing'] + ";"
                                else:
                                    set = settingsvar.strokagrdetaling + itemkeyfeature['keyFeature'] + ";" + \
                                          itemkeyfeature['keyGrDetailing'] + ";"
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
                                                    settingsvar.spisokGrDetailing.append(
                                                        itemkeyfeature['keyGrDetailing'])
                                                    break
                                            else:
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
                            settingsvar.strokagrdetaling = settingsvar.strokagrdetaling + itemkeyfeature[
                                'keyFeature'] + ";"

    if settingsvar.itemstep == 'spisoklist':
        if len(settingsvar.spisoklistdetaling) > 0:
            tmp = []
            for item in settingsvar.spisoklistdetaling:
                item['checkfeat'] = False
                tmp.append(item)
            settingsvar.spisoklistdetaling = tmp
            settingsvar.enddetaling = 'enddetaling'
            if len(settingsvar.spisoknamefeature) > 0: settingsvar.detaling_feature_name = \
                settingsvar.spisoknamefeature[0]
            if len(settingsvar.spisokkeyfeature) > 0: settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
            iduser = funciduser()
            if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
            shablondetaling()
            return
        if len(settingsvar.spisokGrDetailing) > 0:
            settingsvar.ongrupdetaling = True
            settingsvar.enddetaling = 'enddetaling'
            for itemgrdetaling in settingsvar.spisokGrDetailing:
                settingsvar.rest_apiGrDetaling = rest_api(
                    '/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/", '', 'GET')
                addgrGrDetaling()
                settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                settingsvar.detaling_feature_name = settingsvar.spisoknamefeature[0]
                settingsvar.itemdetalingname = ""
                if len(settingsvar.detalingname) > 0: settingsvar.itemdetalingname = settingsvar.detalingname[0]
                iduser = funciduser()
                if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
                shablongrdetaling()
                # del settingsvar.spisokGrDetailing[0]
                if len(settingsvar.detalingname) > 0: del settingsvar.detalingname[0]
                break
        if len(settingsvar.spisoklistdetaling) == 0 and len(settingsvar.spisokGrDetailing) == 0 and len(
                settingsvar.spisokkeyfeature) == 0:
            diagnoz()
    return


# --- вибір деталізації симптому нездужання
def selectdetaling(request, select_kodDetailing):
    settingsvar.spisokkeyinterview.append(select_kodDetailing + ";")
    settingsvar.spisokselectDetailing.append(select_kodDetailing)
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
                settingsvar.spselectnameDetailing.append(item['nameDetailing'])
                del settingsvar.spisoklistdetaling[index]

            index = index + 1
        if len(settingsvar.spisoklistdetaling) > 0:
            shablondetaling()
        else:
            continuegrdetaling(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def continuegrdetaling(request):
    if len(settingsvar.spisokGrDetailing) == 0:
        diagnoz()
    else:
        if settingsvar.continuegrdetaling == False:
            settingsvar.continuegrdetaling = True
            settingsvar.enddetaling = 'enddetaling'
            for itemgrdetaling in settingsvar.spisokGrDetailing:
                settingsvar.rest_apiGrDetaling = rest_api(
                    '/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/", '', 'GET')
                addgrGrDetaling()
                settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
                settingsvar.detaling_feature_name = settingsvar.spisoknamefeature[0]
                if len(settingsvar.detalingname) > 0: settingsvar.itemdetalingname = settingsvar.detalingname[0]
                if len(settingsvar.pacient) > 0: shablonpacient(settingsvar.pacient)
                shablongrdetaling()
                if len(settingsvar.detalingname) > 0: del settingsvar.detalingname[0]
                break
        else:
            return redirect(request.path)
    return


def addgrGrDetaling():
    tmp = []
    for item in settingsvar.rest_apiGrDetaling:
        item['checkfeat'] = False
        tmp.append(item)
    settingsvar.rest_apiGrDetaling = tmp
    return

# ---  вибір деталізації симптому нездужання
def selectgrdetaling(request, select_kodDetailing):
    settingsvar.DiagnozRecomendaciya.append(select_kodDetailing + ";")
    settingsvar.spisokkeyinterview.append(select_kodDetailing + ";")
    settingsvar.spisokselectDetailing.append(select_kodDetailing)
    tmplist = []
    if len(settingsvar.rest_apiGrDetaling) > 0:
        for item in settingsvar.rest_apiGrDetaling:
            if select_kodDetailing != item['kodDetailing']:
                tmplist.append(item)
            else:
                settingsvar.spselectnameDetailing.append(item['nameGrDetailing'])
        settingsvar.rest_apiGrDetaling = tmplist
        settingsvar.nawpage = 'nextgrdetaling'
        if len(settingsvar.rest_apiGrDetaling) > 0:
            shablongrdetaling()
        else:
            if len(settingsvar.spisokGrDetailing) == 0:
                diagnoz()
            else:
                enddetaling(request)
    else:
        diagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- кінець інтервью, пошук та виведення  попереднього діагнозу
def endgrdetaling(request):
    for item in settingsvar.rest_apiGrDetaling:
        if item['checkfeat'] == True:
            settingsvar.continuegrdetaling = False
            break
    endvibor(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def endvibor(request):
    if (settingsvar.viewdetaling == False and len(settingsvar.spisoklistdetaling) > 0):

        if len(settingsvar.spisoklistdetaling) > 0:
            for item in settingsvar.spisoklistdetaling:
                if item['checkfeat'] == True:
                    settingsvar.spisokkeyinterview.append(item['kodDetailing'] + ";")
                    settingsvar.spisokselectDetailing.append(item['kodDetailing'])
                    settingsvar.spselectnameDetailing.append(item['nameDetailing'])
            settingsvar.spisoklistdetaling = []
            continuegrdetaling(request)
            settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
            settingsvar.nawpage = 'nextgrdetaling'
            settingsvar.viewdetaling = True
            del settingsvar.spisokkeyfeature[0]
            del settingsvar.spisoknamefeature[0]

    else:
        if settingsvar.continuegrdetaling == False:
            if len(settingsvar.spisokGrDetailing) > 0:
                settingsvar.continuegrdetaling = True
                for item in settingsvar.rest_apiGrDetaling:
                    if item['checkfeat'] == True:
                        settingsvar.spisokselectDetailing.append(item['kodDetailing'])
                        settingsvar.DiagnozRecomendaciya.append(item['kodDetailing'] + ";")
                        settingsvar.spisokkeyinterview.append(item['kodDetailing'] + ";")
                del settingsvar.spisokGrDetailing[0]
                if len(settingsvar.spisokGrDetailing) > 0:
                    for itemgrdetaling in settingsvar.spisokGrDetailing:
                        settingsvar.rest_apiGrDetaling = rest_api(
                            '/api/GrDetalingController/' + "0/" + itemgrdetaling + "/0/",
                            '', 'GET')
                        addgrGrDetaling()
                        if len(settingsvar.detalingname) > 0: settingsvar.itemdetalingname = settingsvar.detalingname[0]
                        shablongrdetaling()
                        settingsvar.nawpage = 'nextgrdetaling'
                        if len(settingsvar.detalingname) > 0: del settingsvar.detalingname[0]
                        break
                else:
                    settingsvar.spisokkeyfeature = []
                    diagnoz()
            else:
                settingsvar.spisokkeyfeature = []
                settingsvar.spisoknamefeature = []
                diagnoz()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

def enddetaling(request):
    # if len(settingsvar.spisokkeyfeature) > 0:
    if (settingsvar.viewdetaling == False and len(settingsvar.spisoklistdetaling) > 0):
        settingsvar.itemkeyfeature = settingsvar.spisokkeyfeature[0]
        shablondetaling()
        settingsvar.nawpage = 'nextgrdetaling'
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
                if len(settingsvar.detalingname) > 0: settingsvar.itemdetalingname = settingsvar.detalingname[0]
                shablongrdetaling()
                settingsvar.nawpage = 'nextgrdetaling'
                if len(settingsvar.detalingname) > 0: del settingsvar.detalingname[0]
                del settingsvar.spisokGrDetailing[0]

                return render(request, settingsvar.html, context=settingsvar.nextstepdata)
        else:
            if len(settingsvar.spisokkeyfeature) > 0:
                if (settingsvar.itemkeyfeature == settingsvar.spisokkeyfeature[0] and len(
                        settingsvar.spisokkeyfeature) > 0):
                    del settingsvar.spisokkeyfeature[0]
                    del settingsvar.spisoknamefeature[0]
        if len(settingsvar.spisokkeyfeature) > 0:
            settingsvar.itemstep = 'spisokkeyfeature'
            nextstepgrdetaling()
            if len(settingsvar.spisokkeyfeature) == 0 and len(settingsvar.spisoklistdetaling) == 0 and len(
                    settingsvar.spisokGrDetailing) == 0:
                diagnoz()
        else:
            diagnoz()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def shablondetaling():
    iduser = funciduser()
    if len(settingsvar.pacient) > 0:
        shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['detalinglist'] = settingsvar.spisoklistdetaling
    settingsvar.nextstepdata['compl'] = settingsvar.feature_name + ", " + settingsvar.detaling_feature_name
    settingsvar.nextstepdata['next'] = '  Далі '
    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
    settingsvar.nextstepdata['enddetaling'] = settingsvar.enddetaling
    settingsvar.nextstepdata['iduser'] = iduser
    settingsvar.html = 'diagnoz/detaling.html'
    settingsvar.nawpage = 'nextgrdetaling'
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
    settingsvar.nextstepdata['enddetaling'] = settingsvar.enddetaling
    settingsvar.nextstepdata['backurl'] = 'nextgrdetaling'
    settingsvar.nawpage = 'nextgrdetaling'
    settingsvar.html = 'diagnoz/grdetaling.html'

    return


def writediagnoz():
    settingsvar.selectlikar = False

    if settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'listinterwiev':
        saveselectlikar(settingsvar.pacient)
    else:
        if settingsvar.kabinet == 'guest':
            settingsvar.backpage = 'interwievcomplaint'

        if settingsvar.kabinet == 'pacient':
            settingsvar.backpage = 'interwiev'
        for item in settingsvar.diagnozStroka:
            if settingsvar.kodProtokola == item['kodProtokola']:
                contentRecommendation = ''
                api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
                if len(api) > 0:
                    settingsvar.kodDiagnoz = api[0]['kodDiagnoz']
                    apiicd = rest_api('/api/DiagnozController/' + api[0]['kodDiagnoz'] + "/0/0", '', 'GET')
                    if len(apiicd) > 0:
                        if len(apiicd['keyIcd']) > 0: settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
                        settingsvar.icdGrDiagnoz = apiicd['icdGrDiagnoz']
                    apiRecommen = rest_api('/api/RecommendationController/' + api[0]['kodRecommend'] + "/0", '', 'GET')
                    if len(apiRecommen) > 0: settingsvar.contentRecommendation = apiRecommen['contentRecommendation']
                settingsvar.nawpage = 'backfromcontent'
                settingsvar.html = 'diagnoz/versiyadiagnoza.html'

                iduser = funciduser()
                settingsvar.url = item['nametInterview'] + 'як+лікувати'
                settingsvar.namediagnoz = item['nametInterview']
                reason_url = 'https://www.google.com/search'
                search_reason = settingsvar.namediagnoz + '+причини+захворювання'
                likarfamily = []
                if len(settingsvar.pacient) > 0 and settingsvar.kabinet == 'interwiev':
                    likarfamily = rest_api('/api/ControlerFamilyLikar/' + settingsvar.pacient['kodPacient'] + "/0", '',
                                           'GET')
                if len(likarfamily) > 0:
                    settingsvar.html = 'diagnoz/finishinterviewpacient.html'
                    settingsvar.backpage = 'interwiev'
                    for item in likarfamily:
                        likarGrupDiagnoz = rest_api('/api/LikarGrupDiagnozController/'
                                                    + item['kodDoctor'] + '/0', '', 'GET')
                        if len(likarGrupDiagnoz) > 0:
                            for itemdiagnoz in likarGrupDiagnoz:
                                if itemdiagnoz['icdGrDiagnoz'] == settingsvar.icdGrDiagnoz:
                                    settingsvar.likar = rest_api(
                                        '/api/ApiControllerDoctor/' + item['kodDoctor'] + "/0/0", '',
                                        'GET')
                                    if 'name' in settingsvar.likar:
                                        settingsvar.kodDoctor = item['kodDoctor']
                                        settingsvar.namelikar = settingsvar.likar['name'] + " " + settingsvar.likar[
                                            'surname']
                                        #        settingsvar.mobtellikar = CmdStroka['telefon']
                                        settingsvar.likar = settingsvar.likar
                                        medzaklad = rest_api(
                                            '/api/MedicalInstitutionController/' + settingsvar.likar[
                                                'edrpou'] + '/0/0/0', '',
                                            'GET')
                                        settingsvar.namemedzaklad = medzaklad['name']
                                        settingsvar.adrzaklad = medzaklad['adres']
                                        break
                        else:
                            settingsvar.likar = rest_api('/api/ApiControllerDoctor/'
                                                         + item['kodDoctor'] + "/0/0", '', 'GET')
                            settingsvar.kodDoctor = item['kodDoctor']
                            if 'name' in settingsvar.likar:
                                settingsvar.namelikar = settingsvar.likar['name'] + " " + settingsvar.likar['surname']
                                medzaklad = rest_api('/api/MedicalInstitutionController/'
                                                     + settingsvar.likar['edrpou'] + '/0/0/0', '', 'GET')
                                settingsvar.namemedzaklad = medzaklad['name']

                    settingsvar.nextstepdata = {
                        'iduser': iduser,
                        'pacient': 'Увага! ' + settingsvar.pacient['name'] + " " + settingsvar.pacient['surname'],
                        'shapka': 'Ви сформували запит на обстеження у лікаря.',
                        'medzaklad': settingsvar.namemedzaklad + " " + settingsvar.adrzaklad,
                        'likar': 'Ваш призначений лікар: ' + settingsvar.namelikar,
                        # ++ " тел.: ",  settingsvar.mobtellikar,
                        'rekomendaciya': settingsvar.contentRecommendation,
                        'datereception': 'Дата прийому: ' + settingsvar.datereception,
                        'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
                        'backurl': funcbakurl(),
                        'base_url': 'https://www.google.com/search',
                        'search_term': settingsvar.url,
                        'reason_url': reason_url,
                        'search_reason': search_reason
                    }

                else:
                    settingsvar.nextstepdata = {
                        'opis': item['opistInterview'],
                        'http': item['uriInterview'],
                        'rekomendaciya': settingsvar.contentRecommendation,
                        'compl': settingsvar.namediagnoz,
                        'detalinglist': settingsvar.diagnozStroka,
                        'iduser': iduser,
                        'piblikar': '',
                        'base_url': 'https://www.google.com/search',
                        'search_term': settingsvar.url,
                        'backurl': settingsvar.nawpage,
                        'reason_url': reason_url,
                        'search_reason': search_reason,

                    }
                    if len(settingsvar.pacient) > 0:
                        settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                                              settingsvar.pacient['name'] + " " + settingsvar.pacient[
                                                                  'surname']
                    if len(settingsvar.likar) > 0:
                        settingsvar.nextstepdata[
                            'piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
                        settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar

        settingsvar.nextstepdata['fameli'] = True
        if settingsvar.kabinet == 'likarinterwiev': settingsvar.nextstepdata['fameli'] = False
    json = ('IdUser:  ' + settingsvar.kabinet + ', ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: writediagnoz')
    unloadlog(json)
    return


def diagnoz():
    diagnozselect = ""
    settingsvar.itemstep = ""
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
    settingsvar.backpage = 'contentinterwiev'
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
    PacientName = ""
    if len(settingsvar.pacient) > 0:
        PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']
    data = {
        'compl': 'Попередній діагноз: ' + settingsvar.namediagnoz,
        'detalinglist': api,
        'iduser': iduser,
        'backurl': settingsvar.nawpage,
        'pacient': PacientName,

    }
    json = ('IdUser:  ' + settingsvar.kabinet + ', ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: contentinterwiev')
    unloadlog(json)
    return render(request, settingsvar.html, data)


def backdiagnoz(request):
    selectdiagnoz(request, settingsvar.kodProtokola, settingsvar.nametInterview)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


#  --- Кінець блоку  опитування

# --- Блок вибору медзакладу та профільного лікаря
# --- вибір профільного медзакладу

def selectmedzaklad(request, statuszaklad):
    settingsvar.grupmedzaklad = []
    settingsvar.statuszaklad = statuszaklad
    iduser = funciduser()
    match statuszaklad:
        case "2":
            tmp = []
            listlikarfamily = rest_api('/api/ApiControllerDoctor/' + '0/2/0/', '', 'GET')
            if len(listlikarfamily) > 0:
                for item in listlikarfamily:
                    medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '', 'GET')
                    if len(medzaklad) > 0:
                        item['zakladname'] = medzaklad['name']
                        item['adreszak'] = item['uriwebDoctor'] + ', ' + item['email'] + ', тел. ' + item['telefon']
                        item['tel'] = item['telefon']
                    tmp.append(item)
                settingsvar.receptitem = 'receptfamilylikar'
                settingsvar.listlikar = tmp
                selectlikarrofil(tmp)
            else:
                errorprofil('Шановний користувач! За вашим запитом відсутні профільні лікарі.')
            return

        case "5":
            settingsvar.grupDiagnoz = rest_api('/api/MedGrupDiagnozController/' + "0/" +
                                               settingsvar.icdGrDiagnoz + "/0/0", '', 'GET')  # settingsvar.icddiagnoz
            settingsvar.Diagnozmedgrup = settingsvar.grupDiagnoz
            if len(settingsvar.grupDiagnoz) > 0:
                for item in settingsvar.grupDiagnoz:
                    medzaklad = rest_api('/api/MedicalInstitutionController/' + item['kodZaklad'] + '/0/0/0', '', 'GET')
                    if len(medzaklad) > 0:
                        if len(settingsvar.grupmedzaklad) == 0: settingsvar.grupmedzaklad.append(medzaklad)
                        apptru = False
                        for itemmedzaklad in settingsvar.grupmedzaklad:
                            if medzaklad['kodZaklad'] not in itemmedzaklad['kodZaklad']:
                                apptru = False
                            else:
                                apptru = True
                        if apptru == False:  settingsvar.grupmedzaklad.append(medzaklad)
            else:

                settingsvar.grupmedzaklad = rest_api('/api/MedicalInstitutionController/' + '0/0/0/' + statuszaklad,
                                                     '',
                                                     'GET')

    settingsvar.nawpage = 'receptprofillmedzaklad'

    backurl = funcbakurl()
    compl = 'Перелік спеціалізованих медзакладів'
    if statuszaklad == '2': compl = 'Перелік Амбулаторно-поліклінічних закладів'
    settingsvar.html = 'diagnoz/receptionprofilzaklad.html'
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'backurl': backurl,
        'compl': compl,
        'detalinglist': settingsvar.grupmedzaklad,
        'piblikar': '',
        'likar': '',

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
    if settingsvar.kabinet == "guest":
        settingsvar.backpage = "guest"
        settingsvar.kabinetitem = 'receptprofillmedzaklad'


    backreceptprofillmedzaklad(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backreceptprofillmedzaklad(request):
    likargrupdiagnoz = []
    if len(settingsvar.icdGrDiagnoz) > 0:
        if len(settingsvar.kodDoctor) > 0:
            likargrupdiagnoz = rest_api(
                '/api/LikarGrupDiagnozController/' + settingsvar.kodDoctor + "/" + settingsvar.icdGrDiagnoz,
                '', 'GET')
        else:
            likargrupdiagnoz = rest_api(
                '/api/LikarGrupDiagnozController/' + "0/" + settingsvar.icdGrDiagnoz, '', 'GET')

    if settingsvar.kabinetitem == 'likarinterwiev' and len(settingsvar.kodDoctor) > 0 and len(
            likargrupdiagnoz) > 0 and settingsvar.selectlikar == False:
        settingsvar.setintertview = True
        settingsvar.selectlikar = True
        medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '', 'GET')
        settingsvar.namemedzaklad = medzaklad['name']
        settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
        #        settingsvar.mobtellikar = settingsvar.likar['telefon']
        saveselectlikar(settingsvar.pacient)
    else:
        status = "5"
        settingsvar.directdiagnoz = False
        if settingsvar.kabinet == 'guest' or settingsvar.kabinet == 'interwiev':

            match settingsvar.receptitem:
                case 'backreceptprofillmedzaklad':
                    settingsvar.receptitem = 'reception'
                case 'receptprofillmedzaklad':
                    settingsvar.receptitem = 'backreceptprofillmedzaklad'
                case 'interwievcomplaint' | 'receptprofillmedzaklad':
                    settingsvar.receptitem = settingsvar.receptitem
                case 'getsearchcomplateForm':
                    settingsvar.receptitem = 'interwievcomplaint'
                case _:
                    settingsvar.receptitem = 'receptprofillmedzaklad'
            if len(likargrupdiagnoz) > 0 and settingsvar.receptitem == 'interwievcomplaint':
                selectlikarrofil(likargrupdiagnoz)
            else:
                selectmedzaklad(request, status)
        else:
            if settingsvar.kabinet == 'likarinterwiev':
                settingsvar.backpage = 'likarinterwiev'
                settingsvar.receptitem = 'likarinterwiev'
            selectmedzaklad(request, status)
        json = (
                'IdUser: ' + settingsvar.kodPacienta + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
                datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: receptprofillmedzaklad')
        unloadlog(json)
    return


# --- вибір Амбулаторно-поліклінічного закладу до сімейного лікаря
def receptfamilylikar(request):
    status = "2"
    settingsvar.nawpage = 'backsaveselectlikar'
    settingsvar.addinterviewrecept = True
    selectmedzaklad(request, status)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Вибір лікаря серед профільних лікарів незалежно від лікарні де він працює
def selectlikarrofil(listrofillikar):
    settingsvar.listlikar = []
    itemlistlikar = {}
    if settingsvar.receptitem == 'receptfamilylikar' or settingsvar.receptitem == 'selectlikarfamily':
        settingsvar.listlikar = listrofillikar
    else:
        for item in listrofillikar:
            if settingsvar.receptitem != 'familylikar' and settingsvar.receptitem != 'profillikar':
                zakladlikar = rest_api('/api/ApiControllerDoctor/' + item['kodDoctor'] + "/0/0", '', 'GET')
                medzaklad = rest_api('/api/MedicalInstitutionController/' + zakladlikar['edrpou'] + '/0/0/0', '', 'GET')
                itemlistlikar['kodDoctor'] = item['kodDoctor']
                itemlistlikar['kodzaklad'] = zakladlikar['edrpou']
                itemlistlikar['name'] = zakladlikar['name']
                itemlistlikar['surname'] = zakladlikar['surname']
                itemlistlikar['specialnoct'] = zakladlikar['specialnoct']
                itemlistlikar['zakladname'] = medzaklad['name']
                itemlistlikar['adreszak'] = medzaklad['adres']
                itemlistlikar['tel'] = medzaklad['telefon']
            else:
                medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '', 'GET')
                itemlistlikar['kodDoctor'] = item['kodDoctor']
                itemlistlikar['kodzaklad'] = item['edrpou']
                itemlistlikar['name'] = item['name']
                itemlistlikar['surname'] = item['surname']
                itemlistlikar['specialnoct'] = item['specialnoct']
                itemlistlikar['zakladname'] = medzaklad['name']
                itemlistlikar['adreszak'] = medzaklad['adres']
                itemlistlikar['tel'] = medzaklad['telefon']
            settingsvar.listlikar.append(itemlistlikar)
            itemlistlikar = {}


    settingsvar.html = 'diagnoz/selectlikarprofil.html'
    if (settingsvar.kabinet != 'likarinterwiev'
            and settingsvar.kabinet != 'guest' and settingsvar.kabinet != 'interwiev'): settingsvar.receptitem = 'selectedprofillikar'
    iduser = funciduser()
    backurl = funcbakurl()
    workdirection = False
    likarikolegi = False
    dellikar = False
    addfamilylikar = likar = familylikar = False
    compl = 'Перелік спеціалізованих лікарів'
    if settingsvar.receptitem == 'familylikar' or settingsvar.receptitem == 'selectlikarfamily':
        compl = 'Перелік сімейних лікарів'
        workdirection = True

    if settingsvar.backpage == 'receptfamilylikar':
        compl = 'Перелік призначених лікарів'
        workdirection = True
        familylikar = False
        addfamilylikar = True
        dellikar = True
    if settingsvar.backpage == 'addfamilylikar':
        compl = 'Перелік лікарів'
        workdirection = True
        familylikar = True
        likar = False
    if settingsvar.receptitem == 'profillikar':
        workdirection = True

    settingsvar.nextstepdata = {}
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': compl,
        'detalinglist': settingsvar.listlikar,
        'piblikar': '',
        'pacient': '',
        'likar': likar,
        'backurl': backurl,
        'workdirection': workdirection,
        'familylikar': familylikar,
        'namediagnoz': settingsvar.icdGrDiagnoz,
        'likarikolegi': likarikolegi,
        'addfamilylikar': addfamilylikar,
        'dellikar': dellikar,
        'prof_url': 'https://www.google.com/search',
        'medication_url': 'https://www.google.com/search',
        'reason_url': 'https://www.google.com/search',
        'search_prof': settingsvar.namediagnoz + '+профілактика+захворювання',
        'search_reason': settingsvar.namediagnoz + '+причини+захворювання',
        'search_medic': settingsvar.namediagnoz + '+як+лікувати',
    }
    if len(settingsvar.pacient) > 0:
        if settingsvar.receptitem != 'familylikar' and settingsvar.backpage != 'pacientinterwiev' and settingsvar.backpage != 'receptfamilylikar' and settingsvar.backpage != 'addfamilylikar':
            settingsvar.nextstepdata['likar'] = True
        settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                              settingsvar.pacient['name'] + " " + settingsvar.pacient['surname']

    if len(settingsvar.likar) > 0:
        settingsvar.nextstepdata['piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar

    return


# --- Вибір лікаря у профільному мед закладі
def selectdprofillikar(request, selected_kodzaklad, selected_idstatus, selected_name):
    settingsvar.backpage = 'selectdprofillikar'
    settingsvar.gruplikar = []
    settingsvar.kodzaklad = selected_kodzaklad.strip()
    settingsvar.namemedzaklad = selected_name
    settingsvar.idstatus = selected_idstatus.strip()
    medzak = rest_api('/api/MedicalInstitutionController/' + settingsvar.kodzaklad + "/0/0/0", '', 'GET')
    settingsvar.adrzaklad = medzak['adres']
    settingsvar.mobtellikar = medzak['telefon']
    Grupproflikar = rest_api('/api/ApiControllerDoctor/' + "0/" + settingsvar.kodzaklad + "/0", '', 'GET')
    if len(Grupproflikar) > 0:
        if settingsvar.interviewcompl == False and settingsvar.kabinet == 'guest':
            settingsvar.gruplikar = Grupproflikar
        else:
            for item in Grupproflikar:
                match settingsvar.idstatus:
                    case "2":
                        settingsvar.gruplikar.append(item)
                        settingsvar.directdiagnoz = True
                    case "5":
                        settingsvar.likarGrupDiagnoz = rest_api(
                            '/api/LikarGrupDiagnozController/' + item['kodDoctor'] + '/0', '',
                                                'GET')
                        for icdgrdiagnoz in settingsvar.Diagnozmedgrup:
                            for likargrdz in settingsvar.likarGrupDiagnoz:
                                if (likargrdz['icdGrDiagnoz'] in icdgrdiagnoz['icdGrDiagnoz'] and
                                        settingsvar.kodzaklad in icdgrdiagnoz['kodZaklad']):
                                    if len(settingsvar.gruplikar) > 0:
                                        apptru = False
                                        for itemgruplikar in settingsvar.gruplikar:
                                            if itemgruplikar['kodDoctor'] != likargrdz['kodDoctor']:
                                                apptru = False
                                            else:
                                                apptru = True
                                        if apptru == False: settingsvar.gruplikar.append(item)
                                    else:
                                        settingsvar.gruplikar.append(item)
                                    break
        if len(settingsvar.gruplikar) > 0:
            shablonlistlikar()
        else:

            errorprofil('Шановний користувач! За вашим запитом відсутні профільні лікарі.')
            settingsvar.nextstepdata['gruplikar'] = settingsvar.Diagnozmedgrup
            settingsvar.nextstepdata['likargrupdiagnoz'] = settingsvar.likarGrupDiagnoz
            settingsvar.nextstepdata['icdGrDiagnoz'] = settingsvar.icdGrDiagnoz
            settingsvar.nextstepdata['grupproflikar'] = Grupproflikar
            settingsvar.nextstepdata['gruplikar'] = settingsvar.gruplikar
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні профільні лікарі.')
    json = ('IdUser:  ' + settingsvar.kodPacienta + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: selectdprofillikar')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def shablonlistlikar():
    settingsvar.nawpage = 'backlistlikar'
    likar = False
    workdirection = False
    iduser = funciduser()
    backurl = funcbakurl()
    compl = 'Перелік спеціалізованих лікарів'
    directdiagnoz = settingsvar.directdiagnoz
    settingsvar.html = 'diagnoz/selectedprofillikar.html'
    settingsvar.nextstepdata = {}
    if settingsvar.backpage == 'guest' and settingsvar.receptitem == 'receptprofillmedzaklad':
        workdirection = True
    if (
            settingsvar.backpage == 'profillmedzaklad' or settingsvar.backpage == 'selectdprofillikar' or settingsvar.backpage == 'shablonlistlikar') and settingsvar.receptitem == 'directiondiagnoz':
        workdirection = True

    if settingsvar.backpage == 'guest' and settingsvar.receptitem == 'likarworkdirection':
        settingsvar.receptitem = 'receptprofillmedzaklad'
        workdirection = True
    if settingsvar.backpage == 'shablonlistlikar': settingsvar.backpage = 'workdiagnozlikar'
    if settingsvar.kabinet == 'guest' and settingsvar.receptitem == 'receptprofillmedzaklad':
        workdirection = True
    if (settingsvar.kabinet != 'likarinterwiev'
            and settingsvar.kabinet != 'guest' and settingsvar.kabinet != 'interwiev'): settingsvar.receptitem = 'selectedprofillikar'
    if settingsvar.kabinet == 'guest' and settingsvar.receptitem == 'interwievcomplaint':
        settingsvar.backpage = 'interwievcomplaint'
    if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'directiondiagnoz': backurl = 'backlikarworkdiagnoz'
    if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'receptprofillmedzaklad': backurl = 'receptprofillmedzaklad'
    if settingsvar.receptitem == 'likarworkdirection': settingsvar.receptitem = 'receptprofillmedzaklad'
    if settingsvar.receptitem == 'directiondiagnoz': directdiagnoz = False
    if settingsvar.receptitem == 'clinicmedzaklad':
        directdiagnoz = False
        workdirection = True
        compl = 'Перелік лікарів амбулаторно-поліклінічного закладу'

    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': compl,
        'detalinglist': settingsvar.gruplikar,
        'piblikar': '',
        'pacient': '',
        'likar': likar,
        'backurl': backurl,
        'namedzaklad': settingsvar.namemedzaklad,
        'adrdzaklad': settingsvar.adrzaklad,
        'directdiagnoz': directdiagnoz,
        'listapinull': False,
        'workdirection': workdirection,
    }
    if len(settingsvar.pacient) > 0:
        settingsvar.nextstepdata['likar'] = True
        settingsvar.nextstepdata['pacient'] = 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + \
                                              settingsvar.pacient['name'] + " " + settingsvar.pacient['surname']
    if len(settingsvar.likar) > 0:
        settingsvar.nextstepdata['piblikar'] = 'Лікар: ' + settingsvar.namelikar + " тел.: " + settingsvar.mobtellikar
    return


# --- Повернення до списку лікарів
def backlistlikar(request):
    shablonlistlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Функція повернення до початку опитування
def funcbakurl():
    bakurl = 'reception'
    match settingsvar.kabinet:
        case "guest":
            bakurl = 'reception'
        case "pacient" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth':
            bakurl = 'pacient'
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            bakurl = 'likar'
        case "likarprofil":
            bakurl = 'likarprofil'
    return bakurl


# --- Функція повернення до початку опитування
def funciduser():
    iduser = 'Реєстратура'
    match settingsvar.kabinet:
        case "guest":
            iduser = 'Відвідувач'
        case "pacient" | "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth':
            iduser = 'Кабінет пацієнта'
        case "likar" | 'likarprofil' | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
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
    api = rest_api('/api/DependencyDiagnozController/' + "0/" + settingsvar.kodProtokola + "/0", '', 'GET')
    if len(api) > 0:
        settingsvar.kodDiagnoz = api[0]['kodDiagnoz']
        apiicd = rest_api('/api/DiagnozController/' + api[0]['kodDiagnoz'] + "/0/0", '', 'GET')
        settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
        settingsvar.icdGrDiagnoz = apiicd['icdGrDiagnoz']
    for itemzaklad in settingsvar.listlikar:
        if itemzaklad['kodDoctor'] == settingsvar.kodDoctor:
            settingsvar.namemedzaklad = itemzaklad['zakladname']
            settingsvar.adrzaklad = itemzaklad['adreszak']
            settingsvar.namelikar = itemzaklad['name'] + ' ' + itemzaklad['surname']
            settingsvar.datereception = settingsvar.datereception + " " + itemzaklad['tel']
    settingsvar.html = 'diagnoz/finishinterviewpacient.html'
    settingsvar.nawpage = 'backshablonselect'

    if settingsvar.kabinet == 'guest':
        settingsvar.backpage = 'interwievcomplaint'
        settingsvar.nawpage = 'backprofilinterview'
        if settingsvar.receptitem == 'selectlikarfamily': settingsvar.nawpage = 'backsaveselectlikar'
    if settingsvar.kabinet == 'interwiev':
        settingsvar.backpage = 'interwiev'
    if settingsvar.kabinet == 'likarinterwiev':
        settingsvar.receptitem = 'likar'
        settingsvar.backpage = 'likarinterwiev'
    settingsvar.selectlikar = True

    point = settingsvar.icdGrDiagnoz[settingsvar.icdGrDiagnoz.rindex('.', 0):]
    namediagnoz = 'Діагноз : ' + point.replace('.', ' ')

    prof_url = 'https://www.google.com/search'
    search_prof = namediagnoz + '+профілактика+захворювання'
    base_url = 'https://www.google.com/search'
    search_term = namediagnoz + '+як+лікувати'

    settingsvar.namediagnoz = settingsvar.icdGrDiagnoz
    reason_url = 'https://www.google.com/search'
    search_reason = namediagnoz + '+причини+захворювання'

    if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev':
        settingsvar.datereception = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'shapka': 'Увага! сформовано попередній діаноз на обстежені у лікаря.',
            'pacient': 'Пацієнт: ' + pacient['name'] + " " + pacient['surname'],
            'medzaklad': settingsvar.namemedzaklad + " " + settingsvar.adrzaklad,
            'likar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'datereception': 'Дата прийому: ' + settingsvar.datereception,
            'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
            'podval': 'Зберегти опитування?',
            'backurl': backurl,
            'reason_url': reason_url,
            'search_reason': search_reason,
            'base_url': base_url,
            'search_term': search_term,
            'rekomendaciya': settingsvar.contentRecommendation
        }
    else:

        if 'name' in pacient:
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'pacient': 'Увага! ' + pacient['name'] + " " + pacient['surname'],
                'shapka': 'Ви сформували запит на обстеження у лікаря.',
                'medzaklad': settingsvar.namemedzaklad + " " + settingsvar.adrzaklad,
                'likar': 'Лікар: ' + settingsvar.namelikar,  # ++ " тел.: ",  settingsvar.mobtellikar,
                'datereception': 'Дата прийому: ' + settingsvar.datereception,
                'diagnoz': 'Попередній діаноз: ' + settingsvar.nametInterview,
                'podval': 'Ви підтверджуєте свій вибір?',
                'backurl': backurl,
                'reason_url': reason_url,
                'search_reason': search_reason,
                'base_url': base_url,
                'search_term': search_term,
                'rekomendaciya': settingsvar.contentRecommendation
            }
            # settingsvar.kodDoctor = ""

        else:
            settingsvar.html = 'diagnoz/savediagnoz.html'
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'compl': 'Шановний користувач! Ваш профіль не знайдено.',
                'backurl': backurl
            }
    return


def backsaveselectlikar(request):
    saveselectlikar(settingsvar.pacient)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- введення профілю пацієнта для запису на прийом до лікаря
def inputprofilpacient(request, selected_doctor):
    settingsvar.namelikar = ""
    #    settingsvar.mobtellikar = ""
    if "DTR" in selected_doctor: settingsvar.kodDoctor = selected_doctor
    settingsvar.setintertview = True
    CmdStroka = rest_api('/api/ApiControllerDoctor/' + settingsvar.kodDoctor + "/0/0", '', 'GET')
    if 'name' in CmdStroka:
        settingsvar.namelikar = CmdStroka['name'] + " " + CmdStroka['surname']
        #        settingsvar.mobtellikar = CmdStroka['telefon']
        settingsvar.likar = CmdStroka
        medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '', 'GET')
        settingsvar.namemedzaklad = medzaklad['name']
        likarGrupDiagnoz = rest_api('/api/LikarGrupDiagnozController/' +
                                    settingsvar.kodDoctor + '/0', '', 'GET')
        if len(likarGrupDiagnoz) == 0 and settingsvar.receptitem == 'likarinapryamok':
            settingsvar.Onlikarinapryamok = False
            errorprofil('Шановний користувач! за вашим запитом немає робочих напрямків у сімейного лікаря')
        else:
            iduser = funciduser()
            match settingsvar.receptitem:
                case 'receptfamilylikar' | 'profillikar' | 'likarinapryamok' | 'likarinapryamok' | 'familylikar' | 'receptprofillmedzaklad' | 'directiondiagnoz' | 'selectedprofillikar' | 'backreceptprofillmedzaklad':
                    if settingsvar.addinterviewrecept == True and settingsvar.receptitem != 'directiondiagnoz':
                        dateregistrationappointment(request)
                    else:
                        if settingsvar.receptitem == 'receptfamilylikar' and settingsvar.backpage == 'addfamilylikar':
                            writefamilylikar()
                        else:
                            settingsvar.html = 'diagnoz/likarworkdirection.html'
                            backurl = 'receptprofillmedzaklad'
                            settingsvar.nawpage = 'receptprofillmedzaklad'

                            match settingsvar.receptitem:
                                case 'likarinapryamok':
                                    settingsvar.backpage = 'likarinapryamok'
                                case 'profillikar':
                                    settingsvar.backurl = 'profillikar'
                                case 'familylikar':
                                    settingsvar.backurl = 'familylikar'
                                case 'receptprofillmedzaklad':
                                    settingsvar.receptitem = 'likarworkdirection'

                                    settingsvar.likar = {}
                                case 'selectedprofillikar':
                                    settingsvar.receptitem = 'likarworkdiagnoz'
                                case 'directiondiagnoz':
                                    settingsvar.backpage = 'shablonlistlikar'

                                case 'likarworkdirection':
                                    settingsvar.backpage = 'selectedprofillikar'
                                case 'selectfamilylikar':
                                    settingsvar.backpage = 'selectfamilylikar'
                                    backurl = 'selectfamilylikar'
                            if len(likarGrupDiagnoz) > 0:
                                settingsvar.nextstepdata = {
                                    'iduser': iduser,
                                    'complaintlist': likarGrupDiagnoz,
                                    'backurl': backurl,
                                    'piblikar': settingsvar.namelikar,  # + " т." + settingsvar.mobtellikar,
                                    'medzaklad': settingsvar.namemedzaklad,  # + " " + settingsvar.adrzaklad,
                                    'directdiagnoz': settingsvar.directdiagnoz,
                                    'listapinull': True,
                                    'сontentnull': ''
                                }
                            else:
                                settingsvar.nextstepdata = {}
                case 'selectlikarfamily' | 'interwievcomplaint' | 'interwiev' | 'pacientinterwiev' | 'likarinterwiev' | 'getsearchcomplateForm':
                    dateregistrationappointment(request)

                case 'replaceproflikar':
                    if len(settingsvar.itemlikarAdmission) == 0:
                        saveselectlikar(settingsvar.pacient)
                    else:
                        putvisitinglikar()
                        backprofilinterview(request)

    else:
        shablonselect(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def writefamilylikar():
    date_format = "%Y-%m-%d %H:%M:%S"
    dateyear = datetime.now()
    year = dateyear.year
    numbermonth = dateyear.month
    itemdays = dateyear.day
    date_string = str(year) + "-" + str(numbermonth) + "-" + str(
        itemdays) + " 00:00:00"  # "2023-09-23 00:00:00"
    datestart = datetime.strptime(date_string, date_format)
    iso_datestart = datestart.isoformat()
    date_string = str(datetime.min)
    dateend = datetime.strptime(date_string, date_format)
    iso_dateend = dateend.isoformat()
    json = {'Id': 0,
            'KodPacient': settingsvar.kodPacienta,
            'KodDoctor': settingsvar.kodDoctor,
            'Datestart': iso_datestart,
            'Dateend': iso_dateend,
            'Numberrequests': 0,
            'Numberdiagnoz': 0,
            }

    # --- записати в Бд до лікаря
    saveprofil = rest_api('/api/ControlerFamilyLikar/', json, 'POST')
    funcselectfamilylikar()
    return


# --- зміна лікаря у запису на обстеження пацієнта
def putvisitinglikar():
    # --- Змінити лікря у пацієнта
    tmplist = []
    if settingsvar.kabinet == 'likarlistinterwiev':

        json = {'id': 0,
                'KodDoctor': settingsvar.kodDoctor,
                'KodPacient': settingsvar.itemlikarAdmission['kodPacient'],
                'DateVizita': settingsvar.itemlikarAdmission['dateDoctor'],
                'DateInterview': settingsvar.itemlikarAdmission['dateInterview'],
                'KodComplInterv': settingsvar.itemlikarAdmission['kodComplInterv'],
                'KodProtokola': settingsvar.itemlikarAdmission['kodProtokola'],
                'ResultVizita': settingsvar.itemlikarAdmission['resultDiagnoz']
                }

        # --- записати в Бд до лікаря
        saveprofil = rest_api('/api/LifePacientController/', json, 'POST')

        # --- Дописати нового лікря у чергу обстежень до лікаря

        json = {'id': 0,
                'KodDoctor': settingsvar.kodDoctor,
                'KodPacient': settingsvar.itemlikarAdmission['kodPacient'],
                'DateVizita': settingsvar.itemlikarAdmission['dateDoctor'],
                'DateInterview': settingsvar.itemlikarAdmission['dateInterview'],
                'KodComplInterv': settingsvar.itemlikarAdmission['kodComplInterv'],
                'KodProtokola': settingsvar.itemlikarAdmission['kodProtokola'],
                'TopictVizita': settingsvar.itemlikarAdmission['resultDiagnoz'],
                'KodDiagnoz': settingsvar.itemlikarAdmission['kodDiagnoz']
                }
        # --- записати в Бд
        saveprofil = rest_api('/api/ControllerAdmissionPatients/', json, 'POST')

        settingsvar.kodDoctor = settingsvar.itemlikarAdmission['kodDoctor']


    else:
        if len(settingsvar.itemlikarAdmission) > 0:

            saveprofil = rest_api('/api/LifePacientController/' + settingsvar.itemlikarAdmission['kodPacient'] +
                                  '/' + settingsvar.itemlikarAdmission['kodDoctor'] + '/' +
                                  settingsvar.itemlikarAdmission[
                                      'dateInterview'] +
                                  '/' + settingsvar.itemlikarAdmission['kodProtokola'], '', 'GET')

            if len(saveprofil) > 0:
                saveprofil[0]['kodDoctor'] = settingsvar.kodDoctor
                newprofil = saveprofil[0]
                # --- записати в Бд
                saveprofil = rest_api('/api/LifePacientController/', newprofil, 'PUT')

            # --- Змінити лікря у черзі обстежень у лікаря

            saveprofil = rest_api('/api/ControllerAdmissionPatients/' + settingsvar.itemlikarAdmission['kodPacient'] +
                                  '/' + settingsvar.itemlikarAdmission['kodDoctor'] + '/0/0/' +
                                  settingsvar.itemlikarAdmission['dateInterview'] +
                                  '/' + settingsvar.itemlikarAdmission['kodProtokola'], '', 'GET')
            if len(saveprofil) > 0:
                saveprofil[0]['kodDoctor'] = settingsvar.kodDoctor
                newprofil = saveprofil[0]
                # --- записати в Бд
                saveprofil = rest_api('/api/ControllerAdmissionPatients/', newprofil, 'PUT')

            saveprofil = rest_api(
                '/api/RegistrationAppointmentController/' + settingsvar.itemlikarAdmission['kodPacient'] +
                '/' + settingsvar.itemlikarAdmission['kodDoctor'] + '/' + settingsvar.itemlikarAdmission[
                    'dateInterview'] +
                '/' + settingsvar.itemlikarAdmission['kodProtokola'], '', 'GET')

            if len(saveprofil) > 0:
                saveprofil[0]['kodDoctor'] = settingsvar.kodDoctor
                newprofil = saveprofil[0]
                # --- записати в Бд
                saveprofil = rest_api('/api/RegistrationAppointmentController/', newprofil, 'PUT')

            for item in settingsvar.listapi:
                if item['kodPacient'] == settingsvar.itemlikarAdmission['kodPacient'] and item['kodDoctor'] == \
                        settingsvar.itemlikarAdmission['kodDoctor'] and item['dateInterview'] == \
                        settingsvar.itemlikarAdmission['dateInterview'] and item['kodProtokola'] == \
                        settingsvar.itemlikarAdmission['kodProtokola']:
                    item['kodDoctor'] = settingsvar.kodDoctor

                tmplist.append(item)
            settingsvar.listapi = tmplist
        else:

            for item in settingsvar.listapi:
                tmplist.append(item)
                settingsvar.listapi = tmplist
    return


# --- Видалити запис до лікаря на обстеження

def removeappointments(request):
    if settingsvar.kabinet == 'listinterwiev':
        Appointment = rest_api(
            'api/ColectionInterviewController/' + '0/' + settingsvar.itemlikarAdmission['kodPacient'] +
            '/' + settingsvar.itemlikarAdmission['kodDoctor'] + '/' + settingsvar.itemlikarAdmission['dateInterview'] +
            '/' + settingsvar.itemlikarAdmission['kodProtokola'], '', 'DEL')

        funcshablonlistpacient()
    else:
        Appointment = rest_api(
        '/api/RegistrationAppointmentController/' + '0/' + settingsvar.itemlikarAdmission['kodPacient'] +
        '/' + settingsvar.itemlikarAdmission['kodDoctor'] + '/' + settingsvar.itemlikarAdmission['dateInterview'] +
        '/' + settingsvar.itemlikarAdmission['kodProtokola'], '', 'DEL')

        funcshablonlistreceptionlikar()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- функція встановлення відповідного шаблону результатів опитування для гостя пацієнта або лікаря
def shablonselect(request):
    backurl = funcbakurl()
    iduser = funciduser()
    match settingsvar.kabinet:
        case "guest":

            if settingsvar.search == False:
                if request.method == 'POST':
                    form = SearchPacient(request.POST)
                    settingsvar.formsearch = form.data
                    settingsvar.searchpacient = settingsvar.formsearch
                    funcsearchpacient(request, settingsvar.formsearch)
                    settingsvar.search = True
                    request.method = "GET"
                else:
                    settingsvar.setpost = False
                    settingsvar.search = False
                    search_pacient()
            else:
                if len(settingsvar.searchpacient) > 0:
                    funcsearchpacient(request, settingsvar.searchpacient)
                else:
                    settingsvar.setpost = False
                    settingsvar.search = False
                    search_pacient()
        case "pacient" | 'interwiev' | "likar" | 'likarinterwiev' | 'listreceptionlikar':
            saveselectlikar(settingsvar.pacient)

    return


def backshablonselect(request):
    shablonselect(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- функція вибору дати та часу прийому у лікаря
def dateregistrationappointment(request):
    visitinglist = []
    backurl = funcbakurl()
    iduser = funciduser()
    CmdStroka = rest_api('/api/VisitingDaysController/' + settingsvar.kodDoctor + "/0", '', 'GET')
    if len(CmdStroka) > 0:
        settingsvar.html = 'diagnoz/likarappointments.html'
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'likar': settingsvar.setpostlikar,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'complaintlist': CmdStroka,
            'backurl': backurl
        }
    else:
        settingsvar.datereception = " призначається за тел. : " + settingsvar.mobtellikar
        shablonselect(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def selectvisitingdays(request, selected_timevizita, selected_datevizita, selected_daysoftheweek):
    settingsvar.readprofil = True
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

    if 'kodComplInterv' in CmdStroka and CmdStroka['kodComplInterv'] != None:
        kodCompl = CmdStroka['kodComplInterv']
        strind = kodCompl[5:]
        indexdia = int(kodCompl[5:])
        repl = "000000000000"
        indexcmp = "CMP." + repl[0: len(repl) - len(str(indexdia))] + str(indexdia + 1)

    return indexcmp


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
    settingsvar.dateInterview = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    settingsvar.kodComplInterv = SelectNewKodComplInteriew()
    if ';' in settingsvar.spisokselectDetailing:
        details = settingsvar.spisokselectDetailing
    else:
        for item in settingsvar.spisokselectDetailing:
            details = details + item + ';'
    json = {'id': 0,
            'kodDoctor': settingsvar.kodDoctor,
            'kodPacient': settingsvar.kodPacienta,
            'dateInterview': settingsvar.dateInterview,
            'DateDoctor': settingsvar.datereception,
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
    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: savediagnoz')
    unloadlog(json)
    # --- додати проткол опитування
    addColectionInterview()
    # ---  Додати опитування
    addCompletedInterview()
    errorprofil('Шановний користувач! Ваш протокол опитування та попередній діагноз збережено.')
    return render(request, settingsvar.html, settingsvar.nextstepdata)


# перегляд запису до лікаря
def checkvisitinglikar(request):
    settingsvar.funciya = 'checkvisitinglikar'
    settingsvar.kabinet = "guest"
    settingsvar.backpage = 'checkvisitinglikar'
    shablonselect(request)

    return render(request, settingsvar.html, settingsvar.nextstepdata)


# --- кінець  готового блоку


# -------------------------------------------------------------------------
# ---------  Кабінет Пациента

# ---- Функція формування облікового запису  при реєстрації нового користувача (пацієнт або лікар)
def funcaddaccount(login, password):
    details = 'false'
    settingsvar.dateInterview = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    settingsvar.jsonstroka = {'Id': 0,
                              'IdUser': settingsvar.kodPacienta,
                              'IdStatus': '2',
                              'Login': login,
                              'Password': password,
                              'AccountCreatDate': settingsvar.dateInterview,
                              'Subscription': details,
                              }
    saveaccount = rest_api('/api/AccountUserController/', settingsvar.jsonstroka, 'POST')
    return


# --------------------------
# Реєстрація входу до кабінету пацієнта

def reestraccountuser(request):
    settingsvar.html = 'diagnoz/reestraccountuser.html'
    settingsvar.readprofil = False

    if settingsvar.kabinet == "":
        settingsvar.kabinet = 'pacient'
        settingsvar.backpage = 'reestraccountuser'
    if settingsvar.kabinet == "likar":
        settingsvar.backpage = 'reestraccountuser'
    iduser = funciduser()
    if request.method == 'POST':
        if settingsvar.setReestrAccount == False:
            form = ReestrAccountUserForm(request.POST)
            settingsvar.formaccount = form.data
            request.method = 'GET'
            if len(settingsvar.formaccount['login']) > 0:
                numbtel = settingsvar.formaccount['login'][1:]
                if numbtel.isnumeric():
                    if len(numbtel) == 12:
                        if len(settingsvar.formaccount['dwpassword']) == 0:
                            settingsvar.setReestrAccount = False
                            errorprofil('Шановний користувач! Облікові дані не корректно введені')
                        else:
                            if settingsvar.formaccount['password'] != settingsvar.formaccount['dwpassword']:
                                settingsvar.setReestrAccount = False
                                errorprofil('Шановний користувач! Введені паролі не співпадають')
                            else:
                                json = "0/" + settingsvar.formaccount['login'] + "/" + settingsvar.formaccount[
                                    'password'] + '/0'
                                Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                                if len(Stroka) == 0:
                                    Stroka = rest_api(
                                        '/api/AccountUserController/' + "0/" + settingsvar.formaccount[
                                            'login'] + "/0/0", '', 'GET')
                                if len(Stroka) > 0:
                                    settingsvar.setReestrAccount = False
                                    errorprofil('Шановний користувач! Обліковий запис за введеними даними вже існує')
                                else:
                                    backurl = funcbakurl()
                                    doc = rest_api(
                                        'api/PacientController/' + '0/0/0/0/' + settingsvar.formaccount['login'], '',
                                        'GET')
                                    if len(doc) > 0:
                                        settingsvar.zgodayes = True
                                        settingsvar.html = 'diagnoz/pacientprofil.html'
                                        settingsvar.kodPacienta = doc[0]['kodPacient']
                                        settingsvar.pacient = doc[0]
                                        getpostpacientprofil(request)
                                    else:
                                        settingsvar.setReestrAccount = True
                                        settingsvar.setpostlikar = True
                                        settingsvar.html = 'diagnoz/pacientprofil.html'
                                        # form = PacientForm()
                                        initalPacientForm()
                                        form = PacientForm(initial=settingsvar.pacient)
                                        settingsvar.nextstepdata = {
                                            'form': form,
                                            'next': settingsvar.readprofil,
                                            'backurl': backurl,
                                            'iduser': iduser
                                        }
                    else:
                        errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
                else:
                    errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
            else:
                errorprofil("Шановний користувач!  Не введено номер телефону.")
        else:

            pacientprofil(request)

    else:
        reestr = 'Кабінет пацієнта'
        if settingsvar.kabinet == 'guest': reestr = 'Реєстратура'
        if settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev':
            reestr = ''
        if settingsvar.setReestrAccount == False:
            settingsvar.readprofil = False
            formreestraccount = ReestrAccountUserForm()
            settingsvar.nextstepdata = {
                'form': formreestraccount,
                'backurl': 'accountuser',
                'reestrinput': reestr,
                'iduser': iduser
            }
        else:
            pacientprofil(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def initalPacientForm():
    settingsvar.pacient = {'name': "", 'surname': "", 'gender': "чол.", 'age': 5, 'profession': "",
                           'weight': 15, 'growth': 115, 'pind': "xxxxx", 'tel': " +xxx xx xx xxx xx",
                           'email': "ви@example.com"}
    settingsvar.pacient['tel'] = settingsvar.formaccount['login']

    return


# --- клая модальної форми реєстраціїї входу до кабінету пацієнта або лікаря


def accountuser(request):
    backurl = funcbakurl()
    settingsvar.html = 'diagnoz/accountuser.html'
    if settingsvar.setpost == False:
        if request.method == 'POST':
            if settingsvar.searchaccount == True:
                form = SearchPacient(request.POST)
                settingsvar.formsearch = form.data
                if len(settingsvar.formpacient['tel']) > 0:
                    numbtel = settingsvar.formpacient['tel'][1:]
                    if numbtel.isnumeric():
                        if len(numbtel) == 12:
                            funcsearchpacient(request, settingsvar.formsearch)
                            settingsvar.setpost = True
                            settingsvar.readprofil = True
                            request.method = 'GET'
                        else:
                            errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
                    else:
                        errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
                else:
                    errorprofil("Шановний користувач!  Не введено номер телефону.")
            else:
                form = AccountUserForm(request.POST)
                settingsvar.formaccount = form.data
                if len(settingsvar.formaccount['login']) > 0:
                    numbtel = settingsvar.formaccount['login'][1:]
                    if numbtel.isnumeric():
                        if len(numbtel) == 12:

                            json = "0/" + settingsvar.formaccount['login'] + "/" + settingsvar.formaccount[
                                'password'] + '/0'
                            Stroka = rest_api('/api/AccountUserController/' + json, '', 'GET')
                            request.method = 'GET'
                            if len(Stroka) > 0:
                                match settingsvar.kabinetitem:
                                    case "profil" | "pacient" | "interwiev" | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'selectfamilylikar':
                                        settingsvar.kodPacienta = Stroka['idUser']
                                        settingsvar.pacient = rest_api(
                                            '/api/PacientController/' + settingsvar.kodPacienta + '/0/0/0/0',
                                            '', 'GET')
                                        if 'tel' in settingsvar.pacient:
                                            settingsvar.setpost = True
                                            settingsvar.readprofil = True
                                            settingsvar.setpostlikar = True
                                            caseprofil(request)
                                        else:
                                            errorprofil(
                                                'Шановний користувач! За вказаним обліковим записом профіль пацієнта не знайдено.')
                                    case "likar" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarvisitngdays' | 'likarworkdiagnoz' | 'likarlibdiagnoz' | 'likarinapryamok':
                                        settingsvar.kodLikar = Stroka['idUser']
                                        settingsvar.likar = rest_api(
                                            '/api/ApiControllerDoctor/' + settingsvar.kodLikar + '/0/0',
                                            '', 'GET')
                                        if len(settingsvar.likar) > 0:
                                            settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
                                            medzaklad = rest_api(
                                                '/api/MedicalInstitutionController/' + settingsvar.likar[
                                                    'edrpou'] + '/0/0/0', '',
                                                'GET')

                                            settingsvar.namemedzaklad = medzaklad['name']
                                            settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar[
                                                'surname']
                                            #                               settingsvar.mobtellikar = settingsvar.likar['telefon']
                                            settingsvar.statuslikar = medzaklad['idStatus']
                                            settingsvar.setpostlikar = True

                                            if settingsvar.kabinetitem == 'likarinterwiev':
                                                search_pacient()
                                                settingsvar.searchaccount = True
                                            else:
                                                settingsvar.setpost = True
                                                settingsvar.readprofil = True
                                                caseprofil(request)
                                        else:
                                            errorprofil(
                                                'Шановний користувач! За вказаним обліковим записом профіль лікаря не знайдено.')
                            else:
                                errorprofil('Шановний користувач! Невірно введено номер телефону або пароль.')
                        else:
                            errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
                    else:
                        errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
                else:
                    errorprofil("Шановний користувач!  Не введено номер телефону.")
        else:
            cab = 'Кабінет пацієнта'
            backurl = 'pacient'
            compl = 'Реєстрація'
            reestr = True
            if (settingsvar.kabinetitem == "likar" or settingsvar.kabinetitem == 'likarinterwiev'
                    or settingsvar.kabinetitem == 'likarlistinterwiev'
                    or settingsvar.kabinetitem == 'likarreceptionpacient'
                    or settingsvar.kabinetitem == 'likarworkdiagnoz'
                    or settingsvar.kabinetitem == 'likarvisitngdays'
                    or settingsvar.kabinetitem == 'likarlibdiagnoz'):
                cab = 'Кабінет лікаря'
                backurl = 'likar'
                compl = 'Реєстрація '
                reestr = False
            settingsvar.readprofil = False
            settingsvar.formaccount = AccountUserForm()
            settingsvar.nextstepdata = {
                'form': settingsvar.formaccount,
                'compl': compl,
                'reestrinput': cab,
                'backurl': backurl,
                'reestr': reestr
            }
    else:
        caseprofil(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Case входа в вывод соответсвующих списков меню
def caseprofil(request):
    match settingsvar.kabinetitem:
        case 'profil':
            profilinfopacient()

        case 'interwiev':
            shablonlikar(request, settingsvar.pacient)

        case 'listinterwiev':
            shablonforlistinterview()

        case 'listreceptionlikar':
            funcshablonlistreceptionlikar()
        case 'pacientstanhealth':
            shablonforlistreceptionandstanhealth(request)

        case 'likar':
            settingsvar.readprofil = True
            iduser = funciduser()
            likarinfoprofil()
        case 'likarinterwiev':
            if len(settingsvar.pacient) > 0:
                shablonlikar(settingsvar.pacient)
            else:
                settingsvar.searchaccount = True
                search_pacient()
        case 'likarlistinterwiev':
            listlikar()
        case 'likarreceptionpacient':
            listreceptionpacient(request)
        case 'likarworkdiagnoz':
            listworkdiagnoz()
        case 'likarlibdiagnoz':
            listlibdiagnoz()
        case 'likarvisitngdays':
            listlikarvisitngdays()
        case 'likarinapryamok':
            funclikarnapryamok()
        case 'selectfamilylikar':
            funcselectfamilylikar()
    return


# Профіль пацієнта
def profilinfopacient():
    settingsvar.readprofil = True
    settingsvar.html = 'diagnoz/pacientinfoprofil.html'
    registrkabinet = registrprofil = False
    if settingsvar.receptitem == 'registrprofil': registrprofil = True
    if settingsvar.receptitem == 'registrkabinet': registrkabinet = True
    email = ""
    if len(settingsvar.pacient) > 0:
        if len(settingsvar.pacient['email']) != "": email = settingsvar.pacient['email']
        settingsvar.nextstepdata = {
            'namesurname': "Імя, прізвище: " + settingsvar.pacient['name'] + " " + settingsvar.pacient['surname'],
            'gender': 'Стать : ' + settingsvar.pacient['gender'],
            'age': 'Вік(рік.): ' + str(settingsvar.pacient['age']),
            'weight': 'Вага(кг.): ' + str(settingsvar.pacient['weight']),
            'growth': 'Зріст(см.): ' + str(settingsvar.pacient['growth']),
            'profession': 'Профессія: ' + settingsvar.pacient['profession'],
            'pind': 'Поштовий індекс: ' + settingsvar.pacient['pind'],
            'tel': 'Телефон: ' + settingsvar.pacient['tel'],
            'email': 'Поштова електронна адреса: ' + email,
            'registrprofil': registrprofil,
            'registrkabinet': registrkabinet,
        }
    return


# Видалити профіль пацієнта
def deletprofil(request):

    settingsvar.pacient = rest_api(
        '/api/PacientController/' + '0/' + settingsvar.kodPacienta, '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/ColectionInterviewController/' + '0/' + settingsvar.kodPacienta + '/0', '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/RegistrationAppointmentController/' + '0/' + settingsvar.kodPacienta + '/0', '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/PacientMapAnalizController/' + '0/' + settingsvar.kodPacienta, '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/PacientAnalizKroviController/' + '0/' + settingsvar.kodPacienta, '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/PacientAnalizUrineController/' + '0/' + settingsvar.kodPacienta, '', 'DEL')
    settingsvar.pacient = rest_api(
        '/api/AccountUserController/' + '0/' + settingsvar.kodPacienta, '', 'DEL')

    settingsvar.pacient = rest_api(
        '/api/LifePacientController/' + '0/' + settingsvar.kodPacienta + '/0', '', 'DEL')

    settingsvar.pacient = rest_api(
        '/api/ControllerAdmissionPatients/' + '0/' + settingsvar.kodPacienta + '/0', '', 'DEL')




    settingsvar.kabinet = ''
    settingsvar.setintertview = False
    settingsvar.html = 'diagnoz/index.html'
    if settingsvar.receptitem == 'registrprofil': settingsvar.html = 'diagnoz/reception.html'
    settingsvar.nextstepdata = {}
    settingsvar.likar = {}
    settingsvar.pacient = {}
    settingsvar.setpost = False
    settingsvar.datereception = 'призначається за тел:'
    settingsvar.datedoctor = 'не встановлено'
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Формування списку проведених опитувань  для виводу на екран
def shablonforlistinterview():
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.html = 'diagnoz/pacientlistinterwiev.html'
    settingsvar.listapi = []
    settingsvar.listapi = rest_api(
        'api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacienta, '',
        'GET')
    if len(settingsvar.listapi) > 0:

        for item in settingsvar.listapi:
            pacient = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
            if 'name' in pacient:
                item['resultDiagnoz'] = pacient['name'] + ' ' + pacient['surname'] + ' Телефон: ' + pacient['tel']
            api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
            if len(api) > 0:
                item['kodDiagnoz'] = api[0]['kodDiagnoz']
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'backurl': backurl,
            'likar': False,
            'pacient': 'Пацієнт: ' + settingsvar.pacient['profession'] + ' ' + settingsvar.pacient['name']
                       + " " + settingsvar.pacient['surname']
        }
    else:
        errorprofil(
            'Шановний користувач! За вашим запитом відсутні проведені опитування.')

    return


def shablonforlistreceptionandstanhealth(request):
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.listapi = []
    pacientname = settingsvar.pacient['profession'] + ' ' + settingsvar.pacient['name'] + " " + settingsvar.pacient[
        'surname']
    if settingsvar.kabinetitem == 'pacientstanhealth':
        settingsvar.html = 'diagnoz/pacientstanhealth.html'
        settingsvar.listapi = rest_api('api/PacientMapAnalizController/' + settingsvar.kodPacienta + '/0', '', 'GET')
    else:
        settingsvar.html = 'diagnoz/pacientreceptionlikar.html'
        settingsvar.listapi = rest_api('api/RegistrationAppointmentController/' + settingsvar.kodPacienta + '/0/0/0', '',
                                       'GET')
    if len(settingsvar.listapi) > 0:
        settingsvar.pacienthealth = True
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'pacient': pacientname
        }
    else:
        settingsvar.pacienthealth = False
        addpulstisk(request)
    #        errorprofil('Шановний користувач! За вашим запитом відсутня інформація.')
    return


# --- пошуку даних пацієнта
def funcsearchpacient(request, formsearch):
    settingsvar.search = False
    settingsvar.formsearch = ''
    settingsvar.pacient = profilpacient = {}
    json = ""
    if len(formsearch) > 0:
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
        if len(formsearch['name']) == 0 and len(formsearch['surname']) > 0 and len(
                formsearch['telefon']) == 0:
            json = "0/0/0/" + formsearch['surname'] + '/0'
        if len(formsearch['name']) > 0 and len(formsearch['surname']) == 0 and len(
                formsearch['telefon']) > 0:
            json = "0/0/" + formsearch['name'] + '/0/' + formsearch['telefon']
        if len(json) > 0:
            profilpacient = rest_api('api/PacientController/' + json, '', 'GET')

        if len(profilpacient) > 0:
            settingsvar.pacient = profilpacient[0]
            settingsvar.kodPacienta = settingsvar.pacient['kodPacient']
            if (settingsvar.kabinet == "pacient" or settingsvar.kabinet == 'interwiev'
                    or settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev'):
                if settingsvar.kabinet == 'likarinterwiev': settingsvar.backpage = 'receptinterwiev'
                shablonlikar(request, settingsvar.pacient)
            else:
                if settingsvar.funciya == 'checkvisitinglikar':
                    settingsvar.backurl = 'checkvisitinglikar'
                    settingsvar.nextstepdata['iduser'] = 'Реєстратура'
                    funcshablonlistreceptionlikar()

                else:
                    settingsvar.setintertview = True
                    saveselectlikar(settingsvar.pacient)
        else:
            settingsvar.searchpacient = settingsvar.formsearch = ""
            errorprofil('Шановний користувач! За вашим запитом відсутні дані про пацієнта.')
    else:

        shablonlikar(request, settingsvar.pacient)
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
    indexcmp = "PCN.0000000001"
    CmdStroka = rest_api('/api/PacientController/0/0/0/0/0', '', 'GET')

    if 'kodPacient' in CmdStroka and CmdStroka['kodPacient'] != None:
        kodPacient = CmdStroka['kodPacient']
        indexdia = int(kodPacient[5:14])
        repl = "0000000000"
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


# Надання згоди на вкористання персональних даних
def zgoda(request):
    json = ('IdUser: zgoda,' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: zgoda')
    unloadlog(json)
    return render(request, 'diagnoz/persondata.html')

def pacientprofil(request):  # httpRequest
    if settingsvar.zgodayes == False and request.method == 'POST':
        settingsvar.html = 'diagnoz/persondata.html'
        settingsvar.nextstepdata = {}

        settingsvar.zgodayes = True
        if request.method == 'POST':
            form = PacientForm(request.POST)
            settingsvar.formpacient = form.data
            request.method = 'GET'
            if len(settingsvar.formpacient['tel']) > 0 and len(settingsvar.formpacient['name']) > 0 and len(
                    settingsvar.formpacient['surname']) > 0:
                numbtel = settingsvar.formpacient['tel'][1:]
                if numbtel.isnumeric():
                    if len(numbtel) == 12:
                        if int(settingsvar.formpacient['weight']) <= 250 and int(
                                settingsvar.formpacient['weight']) >= 15:
                            if int(settingsvar.formpacient['growth']) <= 230 and int(
                                    settingsvar.formpacient['growth']) >= 115:
                                if int(settingsvar.formpacient['age']) <= 120 and int(
                                        settingsvar.formpacient['age']) >= 5:
                                    settingsvar.jsonformpacient = {'id': 0,
                                                                   'KodPacient': newpacientprofil(),
                                                                   'KodKabinet': "",
                                                                   'Age': settingsvar.formpacient['age'],
                                                                   'Weight': settingsvar.formpacient['weight'],
                                                                   'Growth': settingsvar.formpacient['growth'],
                                                                   'Gender': settingsvar.formpacient['gender'],
                                                                   'Tel': settingsvar.formpacient['tel'],
                                                                   'Email': settingsvar.formpacient['email'],
                                                                   'Name': settingsvar.formpacient['name'],
                                                                   'Surname': settingsvar.formpacient['surname'],
                                                                   'Pind': settingsvar.formpacient['pind'],
                                                                   'Profession': settingsvar.formpacient['profession']
                                                                   }
                                else:
                                    errorprofil(
                                        "Шановний користувач!  Введений показник віку виходить за межі не більше 120р. і не меньше 5р.")
                            else:
                                errorprofil(
                                    "Шановний користувач!  Введений показник росту виходить за межі не вище 230см. і не меньше 115см.")
                        else:
                            errorprofil(
                                "Шановний користувач!  Введений показник ваги виходить за межі не більше 250кг. і не меньше 15кг.")
                    else:
                        errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
                else:
                    errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
            else:
                settingsvar.error = True
                settingsvar.zgodayes = False
                errorprofil("Шановний користувач!  Не введено обов'язкові показника реєстрції профілю.")
        else:
            getpostpacientprofil(request)
    else:
        getpostpacientprofil(request)
    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pacientprofil')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

# функція запису введених показників профілю пацієнта в форматі масиву для вдображення в шаблонах
def modformatjson(formdata):
    settingsvar.pacient = {'id': 0,
                           'kodPacient': newpacientprofil(),
                           'kodKabinet': "",
                           'age': formdata['age'],
                           'weight': formdata['weight'],
                           'growth': formdata['growth'],
                           'gender': formdata['gender'],
                           'tel': formdata['tel'],
                           'email': formdata['email'],
                           'name': formdata['name'],
                           'surname': formdata['surname'],
                           'pind': formdata['pind'],
                           'profession': formdata['profession']
                           }
    settingsvar.readprofil = True
    return


# --- записати в Бд введенний профіль
def addprofilpacient(request):
    if settingsvar.receptitem == 'registrkabinet':
        log = settingsvar.formaccount['login']
        pas = settingsvar.formaccount['password']
        funcaddaccount(log, pas)
        errorprofil('Шановний користувач!  Ваш обліковий запис збережено.')
        settingsvar.nextstepdata = {}
        settingsvar.html = 'diagnoz/reception.html'

    if settingsvar.receptitem == 'registrprofil':
        doc = rest_api('api/PacientController/' + '0/0/0/0/' + settingsvar.jsonformpacient['Tel'], '', 'GET')
        if len(doc) == 0:
            settingsvar.pacient = rest_api('/api/PacientController/', settingsvar.jsonformpacient, 'POST')
            if len(settingsvar.pacient) > 0:
                errorprofil('Шановний користувач!  Ваш профіль збережено.')
                settingsvar.nextstepdata = {}
                settingsvar.html = 'diagnoz/reception.html'
        else:
            settingsvar.kodPacienta = doc[0]['kodPacient']
            settingsvar.pacient = doc[0]
            errorprofil('Шановний користувач!  Ваш профіль вже існує в БД.')

    json = ('IdUser: addprofilpacient' + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: addprofilpacient')
    unloadlog(json)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Знайдено реєструємий профіль в Бд змінити показники
def repetpacientprofil(request):
    getpostpacientprofil(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Активувати коригування профілю пацієнта
def editpacientprofil(request):
    if settingsvar.receptitem == 'registrprofil':
        settingsvar.editpacientprofil = True
        if settingsvar.editprofil == True: settingsvar.editpacientprofil = False
        getpostpacientprofil(request)
    else:
        pacientprofil(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Введення та коригування профілю пацієнта
def getpostpacientprofil(request):
    settingsvar.html = 'diagnoz/pacientprofil.html'
    iduser = funciduser()
    backurl = funcbakurl()
    if settingsvar.kabinetitem != 'likarinterwiev': settingsvar.kabinetitem = 'profil'
    if (request.method == 'POST' or settingsvar.zgodayes == True) and settingsvar.editpacientprofil != True:
        if request.method == 'POST':
            form = PacientForm(request.POST)
            settingsvar.formpacient = form.data
            settingsvar.pacient = {}
            if len(settingsvar.formpacient['tel']) > 0 and len(settingsvar.formpacient['name']) > 0 and len(
                    settingsvar.formpacient['surname']) > 0:
                numbtel = settingsvar.formpacient['tel'][1:]
                if numbtel.isnumeric():
                    if len(numbtel) == 12:
                        if int(settingsvar.formpacient['weight']) <= 250 and int(
                                settingsvar.formpacient['weight']) >= 15:
                            if int(settingsvar.formpacient['growth']) <= 230 and int(
                                    settingsvar.formpacient['growth']) >= 115:
                                if int(settingsvar.formpacient['age']) <= 120 and int(
                                        settingsvar.formpacient['age']) >= 5:
                                    settingsvar.jsonformpacient = {'id': 0,
                                                                   'KodPacient': newpacientprofil(),
                                                                   'KodKabinet': "",
                                                                   'Age': settingsvar.formpacient['age'],
                                                                   'Weight': settingsvar.formpacient['weight'],
                                                                   'Growth': settingsvar.formpacient['growth'],
                                                                   'Gender': settingsvar.formpacient['gender'],
                                                                   'Tel': settingsvar.formpacient['tel'],
                                                                   'Email': settingsvar.formpacient['email'],
                                                                   'Name': settingsvar.formpacient['name'],
                                                                   'Surname': settingsvar.formpacient['surname'],
                                                                   'Pind': settingsvar.formpacient['pind'],
                                                                   'Profession': settingsvar.formpacient['profession']
                                                                   }
                                else:
                                    errorprofil(
                                        "Шановний користувач!  Введений показник віку виходить за межі не більше 120р. і не меньше 5р.")
                                    settingsvar.zgodayes = False
                                    return
                            else:
                                errorprofil(
                                    "Шановний користувач!  Введений показник росту виходить за межі не вище 230см. і не меньше 115см.")
                                settingsvar.zgodayes = False
                                return
                        else:
                            errorprofil(
                                "Шановний користувач!  Введений показник ваги виходить за межі не більше 250кг. і не меньше 15кг.")
                            settingsvar.zgodayes = False
                            return
                    else:
                        errorprofil("Шановний користувач!  Номер телефону меньше 12 цифр.")
                        settingsvar.zgodayes = False
                        return
                else:
                    errorprofil("Шановний користувач!  Номер телефону містить не цифрові символи.")
                    settingsvar.zgodayes = False
                    return
            else:
                settingsvar.error = True
                settingsvar.zgodayes = False
                errorprofil("Шановний користувач!  Не введено обов'язкові показника реєстрції профілю.")
                return

        match settingsvar.kabinet:
            case 'guest':
                if len(settingsvar.pacient) == 0 and settingsvar.receptitem != 'registrkabinet':
                    modformatjson(settingsvar.formpacient)
                if settingsvar.receptitem == 'registrprofil' or settingsvar.receptitem == 'registrkabinet':
                    settingsvar.editprofil = False
                    profilinfopacient()
                else:
                    saveselectlikar(settingsvar.pacient)
            case 'pacient' | 'interwiev':
                if settingsvar.editprofil == False:
                    # --- записати в Бд облікові дані

                    Stroka = rest_api('/api/AccountUserController/' + "0/" + settingsvar.formpacient['tel'] + "/0/0",
                                      '', 'GET')
                    if len(Stroka) == 0:
                        log = settingsvar.formaccount['login']
                        pas = settingsvar.formaccount['password']
                        funcaddaccount(log, pas)

                    # --- записати в Бд введенний профіль
                    doc = rest_api('api/PacientController/' + '0/0/0/0/' + settingsvar.formpacient['tel'], '',
                                   'GET')
                    if len(doc) == 0:
                        settingsvar.pacient = rest_api('/api/PacientController/', settingsvar.jsonformpacient, 'POST')
                    else:
                        settingsvar.pacient = doc[0]
                    settingsvar.setpost = True
                    if settingsvar.backpage == 'home_view':
                        funcpacient()
                    else:
                        shablonlikar(request, settingsvar.pacient)
                else:
                    if len(settingsvar.pacient) > 0:
                        settingsvar.jsonformpacient['id'] = settingsvar.pacient['id']
                        settingsvar.jsonformpacient['KodPacient'] = settingsvar.pacient['kodPacient']
                        settingsvar.kodPacienta = settingsvar.pacient['kodPacient']
                        settingsvar.pacient = rest_api('/api/PacientController/', json, 'PUT')
                        settingsvar.editprofil = False
                    if settingsvar.kabinet == 'pacient': settingsvar.html = 'diagnoz/pacient.html'
            case 'likarinterwiev':
                if len(settingsvar.pacient) > 0:
                    if settingsvar.readprofil != False:
                        saveselectlikar(settingsvar.pacient)
                else:
                    modformatjson(settingsvar.formpacient)
                    shablonlikar(request, settingsvar.pacient)
            case _:
                modformatjson(settingsvar.formpacient)
                settingsvar.setpost = True
                settingsvar.setpostlikar = True
                errorprofil('Шановний користувач!  Ваш обліковий запис та профіль збережено.')
    else:

        if settingsvar.kabinetitem == 'likarinterwiev': backurl = 'likar'
        if len(settingsvar.pacient) > 0:
            settingsvar.readprofil = False
            settingsvar.editprofil = True
            settingsvar.editpacientprofil = False
            form = PacientForm(initial=settingsvar.pacient)
            settingsvar.nextstepdata = {
                'form': form,
                'next': settingsvar.readprofil,
                'backurl': backurl,
                'iduser': iduser
            }
        else:
            form = PacientForm()
            if settingsvar.error == True:
                form = PacientForm(initial=settingsvar.formpacient)
                settingsvar.error = False
            settingsvar.nextstepdata = {
                'form': form,
                'next': False,
                'backurl': backurl,
                'iduser': iduser
            }
    return


# --- Функція формування реквізитів профілю пацієнта для відображення на вебсайті
def shablonlikar(request, profilpacient):
    settingsvar.readprofil = True
    backurl = funcbakurl()
    settingsvar.html = 'diagnoz/receptinterwiev.html'
    shablonpacient(profilpacient)
    funsearchcomplform(request)
    if settingsvar.receptitem == 'receptinterwiev': backurl = 'receptinterwiev'
    settingsvar.nextstepdata['complaintlist'] = settingsvar.сomplaintselect
    settingsvar.nextstepdata['backurl'] = backurl
    settingsvar.nextstepdata['likar'] = settingsvar.readprofil = True
    settingsvar.nextstepdata['form'] = settingsvar.formsearchtext
    return


def shablonpacient(profilpacient):
    iduser = funciduser()
    backurl = funcbakurl()
    pind = mail = tel = ''
    if len(profilpacient) > 0:
        if profilpacient['tel'] != "": tel = profilpacient['tel']
        if profilpacient['email'] != "": mail = profilpacient['email']
        if profilpacient['pind'] != "": pind = profilpacient['pind']
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
    next = 'Повторити запит'
    if 'існує' in compl: next = 'Далі'
    if 'лікар' in compl: next = 'Далі'
    if len(settingsvar.likar) > 0:
        if settingsvar.kabinet == "likarlistinterwiev" or settingsvar.kabinet == "likarreceptionpacient":
            iduser = 'Лікар: ' + settingsvar.likar['name'] + settingsvar.likar['surname']

    if settingsvar.kabinet == "pacient" and settingsvar.backpage == 'selectfamilylikar':  backurl = 'pacient'
    if settingsvar.kabinet == "guest" and settingsvar.backpage == "checkvisitinglikar":  backurl = 'backshablonselect'
    if settingsvar.kabinet == "guest" and settingsvar.receptitem != 'registrprofil': backurl = 'backshablonselect'
    if settingsvar.kabinet == "guest" and settingsvar.receptitem == 'registrprofil': backurl = 'repetpacientprofil'
    if settingsvar.kabinet == "guest" and settingsvar.receptitem == 'registrkabinet': backurl = 'reestraccountuser'
    if settingsvar.kabinet == 'listinterwiev' or settingsvar.kabinet == 'interwiev' or settingsvar.kabinet == 'listreceptionlikar' or settingsvar.kabinet == 'pacientstanhealth': backurl = 'pacient'
    if settingsvar.kabinet == 'pacient': backurl = 'reestraccountuser'
    if settingsvar.kabinet == "guest" and settingsvar.receptitem == 'clinicmedzaklad': backurl = 'reception'
    if settingsvar.kabinet == "" and settingsvar.backpage == 'home_view': settingsvar.backpage = 'index'

    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': compl,
        'backurl': backurl,
        'next': next

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

    # --- додати звернення в Бд до лікаря
    familylikar = rest_api('/api/ControlerFamilyLikar/' + settingsvar.kodPacienta + "/" + settingsvar.kodDoctor, '',
                           'GET')
    if len(familylikar) > 0:
        likar = familylikar[0]
        likar['numberrequests'] = likar['numberrequests'] + 1
        saveprofil = rest_api('/api/ControlerFamilyLikar/', likar, 'PUT')
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
            'KodDiagnoz': settingsvar.kodDiagnoz
            }
    # --- записати в Бд
    saveprofil = rest_api('/api/RegistrationAppointmentController/', json, 'POST')
    return


def addAdmissionPatientsLikar():
    json = {'id': 0,
            'KodDoctor': settingsvar.kodDoctor,
            'KodPacient': settingsvar.kodPacienta,
            'DateVizita': settingsvar.datereception,
            'DateInterview': settingsvar.dateInterview,
            'KodComplInterv': settingsvar.kodComplInterv,
            'KodProtokola': settingsvar.kodProtokola,
            'TopictVizita': 'Підтвердження попереднього діагнозу, призначення плану лікування.',
            'KodDiagnoz': settingsvar.kodDiagnoz
            }
    # --- записати в Бд
    saveprofil = rest_api('/api/ControllerAdmissionPatients/', json, 'POST')
    return


# --- Збереження протоколу опитування та запису до лікаря
def saveraceptionlikar(request):  # httpRequest
    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: saveraceptionlikar')
    unloadlog(json)
    settingsvar.addinterviewrecept = False
    # --- додати проткол опитування
    addColectionInterview()
    # ---  Додати опитування
    addCompletedInterview()
    # ---  Додати запис до лікаря в історії пацієнта
    addReceptionPacient()
    # ---  Додати запис до лікаря протоколу опитування пацієнта
    addReceptionLikar()
    # ---  Додати запис до лікаря в розклад прийому лікаря
    addAdmissionPatientsLikar()
    if settingsvar.kabinet == 'guest' and len(settingsvar.pacient) > 0:
        # --- записати в Бд введенний профіль
        doc = rest_api('api/PacientController/' + '0/0/0/0/' + settingsvar.pacient['tel'], '', 'GET')
        if len(doc) == 0:
            settingsvar.pacient = rest_api('/api/PacientController/', settingsvar.pacient, 'POST')

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
    settingsvar.kabinet = 'pacient'
    settingsvar.backpage = 'pacientprofil'
    iduser = funciduser()
    if settingsvar.setpost == False:
        accountuser(request)
        settingsvar.initialprofil = True
    else:

        if settingsvar.initialprofil == True:
            settingsvar.html = 'diagnoz/pacient.html'
            settingsvar.initialprofil = False
        else:
            settingsvar.html = 'diagnoz/pacientprofil.html'
            settingsvar.readprofil = True
            settingsvar.initialprofil = True
        profilinfopacient()
    json = ('IdUser: ' + settingsvar.kodPacienta + ', ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: profilpacient')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Провести опитування пациєнта в особистому кабінеті
def pacientinterwiev(request):  # httpRequest
    backpacientinterwiev(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backpacientinterwiev(request):
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev'
            or settingsvar.kabinet == 'likarreceptionpacient'
            or settingsvar.kabinet == 'likarworkdiagnoz'
            or settingsvar.kabinet == 'likarvisitngdays'
            or settingsvar.kabinet == 'likarlibdiagnoz'):

        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'receptinterwiev'
        settingsvar.kabinetitem = 'interwiev'
        settingsvar.kabinet = 'interwiev'
        settingsvar.receptitem = 'pacientinterwiev'
        settingsvar.backpage = 'pacientinterwiev'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            shablonlikar(request, settingsvar.pacient)

    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pacientinterwiev')
    unloadlog(json)
    return


# --- функція розподілу на профіль інтервью або на вибір лікаря
def addreceptpacientlikar(request):
    settingsvar.addinterviewrecept = True
    funcshablonlistpacient()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Вибір медзакладу згідно до діагнозу інтервью
def selectmedzakladpacien():
    api = rest_api('/api/DependencyDiagnozController/' + "0/" + settingsvar.kodProtokola + "/0", '', 'GET')
    if len(api) > 0:
        settingsvar.kodDiagnoz = api[0]['kodDiagnoz']
        apiicd = rest_api('/api/DiagnozController/' + api[0]['kodDiagnoz'] + "/0/0", '', 'GET')
        settingsvar.icddiagnoz = apiicd['keyIcd'][:16]
        settingsvar.icdGrDiagnoz = apiicd['icdGrDiagnoz']

        settingsvar.grupDiagnoz = rest_api('/api/MedGrupDiagnozController/' + "0/" +
                                           settingsvar.icdGrDiagnoz + "/0/0", '', 'GET')  # settingsvar.icddiagnoz

        if len(settingsvar.grupDiagnoz) > 0:
            for item in settingsvar.grupDiagnoz:
                medzaklad = rest_api('/api/MedicalInstitutionController/' + item['kodZaklad'] + '/0/0/0', '', 'GET')
                if len(medzaklad) > 0:
                    if len(settingsvar.grupmedzaklad) == 0: settingsvar.grupmedzaklad.append(medzaklad)
                    apptru = False
                    for itemmedzaklad in settingsvar.grupmedzaklad:
                        if medzaklad['kodZaklad'] not in itemmedzaklad['kodZaklad']:
                            apptru = False
                    else:
                        apptru = True
                if apptru == False:  settingsvar.grupmedzaklad.append(medzaklad)
        else:
            #                if settingsvar.kabinet == 'guest':
            settingsvar.grupmedzaklad = rest_api(
                '/api/MedicalInstitutionController/' + '0/0/0/' + settingsvar.statuszaklad, '', 'GET')
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


# --- Профіль проведеного інтервью
def profilinterview(request, selected_protokol, selected_datevizita, selected_kodDiagnoz,
                    selected_dateInterview):  # httpRequest
    settingsvar.datevizita = selected_datevizita
    settingsvar.dateInterview = selected_dateInterview
    settingsvar.kodProtokola = selected_protokol
    settingsvar.kodDiagnoz = selected_kodDiagnoz
    settingsvar.backpage = 'profilinterview'
    if settingsvar.kabinet != 'listreceptionlikar': settingsvar.backpage = 'profilinterview'

    settingsvar.nametInterview = ""
    settingsvar.idinterview = ""
    for item in settingsvar.listapi:
        if settingsvar.kodProtokola == item['kodProtokola']:
            match settingsvar.kabinet:
                case 'pacientlistinterwiev' | 'listinterwiev' | 'likarlistinterwiev':
                    settingsvar.nametInterview = item['nameInterview']
                case 'listreceptionlikar' | 'checkvisitinglikar':
                    if settingsvar.addinterviewrecept == True:
                        settingsvar.nametInterview = item['nameInterview']
                        settingsvar.spisokselectDetailing = item['detailsInterview']
                        settingsvar.resultDiagnoz = item['resultDiagnoz']
                    else:
                        settingsvar.nametInterview = item['diagnoz']
            if selected_dateInterview == item['dateInterview']:
                settingsvar.idinterview = str(item['id'])
                settingsvar.itemlikarAdmission = item
                break
    if settingsvar.kodProtokola.find('PRT.') < 0:
        match settingsvar.kabinet:
            case 'pacient':
                settingsvar.html = 'diagnoz/pacient.html'
                settingsvar.nextstepdata = {}
            case 'pacientlistinterwiev':
                pacientlistinterwiev(request)
            case 'listreceptionlikar':
                selectmedzakladpacien()
            case 'likar':
                settingsvar.html = 'diagnoz/likar.html'
                settingsvar.nextstepdata = {}
            case 'likarlistinterwiev':
                likarlistinterwiev(request)
            case 'guest' | 'interwiev' | 'listinterwiev' | 'likarinterwiev' | 'likarreceptionpacient' | 'checkvisitinglikar':
                funcshablonlistpacient()
    else:
        if settingsvar.addinterviewrecept == True:
            settingsvar.datereception = settingsvar.datevizita
            settingsvar.kodDoctor = settingsvar.itemlikarAdmission['kodDoctor']
            settingsvar.kodComplInterv = settingsvar.itemlikarAdmission['kodComplInterv']
            addReceptionLikar()
            settingsvar.addinterviewrecept = False
            funcshablonlistreceptionlikar()
        else:
            nextprofilinterview(request)

    json = (
                'IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodPacienta + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: profilinterview')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def nextprofilinterview(request):
    likarName = ""
    PacientName = ""
    dateint = ""
    remove = False
    removefunc = ""
    backurl = ""
    select_dateDoctor = " призначається за тел. : " + settingsvar.mobtellikar
    match settingsvar.kabinet:

        case 'listinterwiev':
            settingsvar.setpostlikar = False
            settingsvar.backurl = funcbakurl()
            funcshablonlistpacient()
        case 'likarlistinterwiev':
            # listlikar()
            removefunc = 'removeinterview'
            remove = True
    match settingsvar.kabinetitem:

        case "guest":
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'checkvisitinglikar'
            removefunc = 'removeinterview'
            remove = True
            if settingsvar.backurl == 'checkvisitinglikar':
                settingsvar.backpage = 'checkvisitinglikar'

        case "profil" | "pacient" | "interwiev" | 'listinterwiev':
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'pacientlistinterwiev'
            removefunc = 'removeinterview'
            remove = True
        case 'listreceptionlikar':
            settingsvar.nawpage = 'pacientreceptionlikar'
            backurl = 'pacientreceptionlikar'
            removefunc = 'removeinterview'
            remove = True
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'likarlistinterwiev'
        case 'likarreceptionpacient':
            settingsvar.nawpage = 'backprofilinterview'
            backurl = 'likarreceptionpacient'
            removefunc = 'removeinterview'
            remove = True

    iduser = funciduser()
    likarName = ""
    medzaklad = ''
    for item in settingsvar.listapi:

        booldatevizita = False
        if settingsvar.kabinetitem == 'likarreceptionpacient':
            if item['dateVizita'] == settingsvar.datevizita:
                booldatevizita = True
        else:
            booldatevizita = True
        if booldatevizita == True:

            if settingsvar.kodProtokola == item['kodProtokola'] and settingsvar.dateInterview == item['dateInterview']:
                match settingsvar.kabinetitem:
                    case 'likarreceptionpacient':
                        if item['dateVizita'] != None:
                            select_dateDoctor = item['dateVizita']
                    case "profil" | "pacient" | "interwiev" | 'listinterwiev' | "likar" | 'likarinterwiev' | 'likarlistinterwiev' | 'listreceptionlikar' | 'guest':
                        if (item['dateDoctor'] != None):
                            select_dateDoctor = item['dateDoctor']
                dateint = item['dateInterview']
                doc = {}
                medzak = {}
                match settingsvar.kabinetitem:

                    case "profil" | "pacient" | "interwiev" | 'listinterwiev' | 'listreceptionlikar' | 'guest':
                        if item['kodDoctor'] != None and len(item['kodDoctor']) > 0:
                            doc = rest_api('api/ApiControllerDoctor/' + item['kodDoctor'] + '/0/0', '', 'GET')
                            likarName = ''
                            if len(doc) > 0:
                                likarName = doc['name'] + ' ' + doc['surname']  # + ' Телефон: ' + doc['telefon']
                        settingsvar.PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']

                        medzak = rest_api('/api/MedicalInstitutionController/' + doc['edrpou'] + "/0/0/0", '', 'GET')

                        if len(medzak) > 0: medzaklad = medzak['name']

                    case "likar" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient':
                        if item['kodPacient'] != None and len(item['kodPacient']) > 0:
                            doc = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
                            settingsvar.kodPacienta = item['kodPacient']
                            settingsvar.pacientName = doc['name'] + ' ' + doc['surname'] + ' Телефон: ' + doc['tel']
                        likarName = settingsvar.namelikar  # + " тел.: " + settingsvar.mobtellikar
                        settingsvar.pacient = doc
                        medzaklad = settingsvar.namemedzaklad
                break
    depend = rest_api('api/DependencyDiagnozController/' + '0/' + settingsvar.kodProtokola + '/0', '', 'GET')
    recommend = {}

    if len(depend) > 0:
        recommend = rest_api('api/RecommendationController/' + depend[0]['kodRecommend'] + '/0', '', 'GET')
        diagnoz = rest_api('api/DiagnozController/' + depend[0]['kodDiagnoz'] + '/0/0', '', 'GET')
        urlinet = diagnoz['uriDiagnoza']
        if settingsvar.nametInterview == "": settingsvar.nametInterview = diagnoz['nameDiagnoza']
        settingsvar.namediagnoz = 'Попередній діагноз: ' + diagnoz['nameDiagnoza']
    else:
        recommend['contentRecommendation'] = ''
        diagnoz = rest_api('api/InterviewController/' + settingsvar.kodProtokola + '/0/0/0/0', '', 'GET')
        if len(diagnoz) > 0:
            urlinet = diagnoz[0]['uriInterview']
            if settingsvar.nametInterview == "": settingsvar.nametInterview = diagnoz[0]['nametInterview']
            settingsvar.namediagnoz = 'Попередній діагноз: ' + diagnoz[0]['nametInterview']
        else:
            diagnoz = rest_api('api/DiagnozController/' + settingsvar.kodDiagnoz + '/0/0', '', 'GET')
            urlinet = diagnoz['uriDiagnoza']
            if settingsvar.nametInterview == "": settingsvar.nametInterview = diagnoz['nameDiagnoza']
            settingsvar.namediagnoz = 'Попередній діагноз: ' + diagnoz['nameDiagnoza']


    settingsvar.html = 'diagnoz/profilinterview.html'
    settingsvar.backpage = 'profilinterview'
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['namepacient'] = 'Пацієнт:        ' + settingsvar.pacientName
    settingsvar.nextstepdata['namelikar'] = 'Лікар:          ' + likarName
    settingsvar.nextstepdata['medzaklad'] = 'Мед. заклад: ' + medzaklad
    settingsvar.nextstepdata['dateinterv'] = 'Дата опитування: ' + dateint
    settingsvar.nextstepdata['datereception'] = 'Дата прийому:   ' + select_dateDoctor
    settingsvar.nextstepdata['diagnoz'] = settingsvar.namediagnoz
    settingsvar.nextstepdata['recomendaciya'] = 'Рекомендації:   ' + recommend['contentRecommendation']
    settingsvar.nextstepdata['urlinet'] = 'Опис в інтернеті:   ' + urlinet
    settingsvar.nextstepdata['backurl'] = backurl
    settingsvar.nextstepdata['remove'] = remove
    settingsvar.nextstepdata['removefunc'] = removefunc
    settingsvar.nextstepdata['likar'] = settingsvar.setpostlikar
    settingsvar.url = settingsvar.nametInterview + '+як+лікувати'
    settingsvar.nextstepdata['base_url'] = 'https://www.google.com/search'
    settingsvar.nextstepdata['search_term'] = settingsvar.url

    return


def backprofilinterview(request):
    nextprofilinterview(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def removeinterview(request):
    match settingsvar.kabinetitem:
        case 'listinterwiev':
            settingsvar.listapi = rest_api('api/ColectionInterviewController/' + settingsvar.idinterview + '/0/0', '',
                                           'DEL')
            if len(settingsvar.listapi) > 0:
                funcshablonlistpacient()
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev':
            settingsvar.listapi = rest_api('api/ColectionInterviewController/' + settingsvar.idinterview + '/0/0', '',
                                           'DEL')
            if len(settingsvar.listapi) > 0:
                listlikar()
        case 'listreceptionlikar':
            settingsvar.listapi = rest_api('api/RegistrationAppointmentController/' + settingsvar.idinterview + '/0/0',
                                           '',
                                           'DEL')
            if len(settingsvar.listapi) > 0:
                funcshablonlistreceptionlikar()
        case 'likarreceptionpacient':
            settingsvar.listapi = rest_api('api/ControllerAdmissionPatients/' + settingsvar.idinterview + '/0/0', '',
                                           'DEL')
            if len(settingsvar.listapi) > 0:
                listreceptionpacient()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def recomentaktikhealing(request):
    # Открыть Google в браузере по умолчанию

    # Укажите путь к исполняемому файлу браузера
    #    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    #    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

    # Используйте зарегистрированный браузер
    #    webbrowser.get('chrome').open_new_tab('https://www.google.com/search?q=Сердечная+недостаточность+тактика+лечения')

    #    url = settingsvar.url        #"https://www.python.org"
    #    js_code = f'window.open("{url}", "_blank");'
    #    display(Javascript(js_code))

    #    driver = webdriver.Chrome()
    #    driver.get(settingsvar.url)

    #    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
    #    b=  webbrowser.get('chrome')
    #    b.open_new_tab(settingsvar.url)
    #    webbrowser.open(settingsvar.url)

    #        'https://www.google.com/search?q=Сердечная+недостаточность+тактика+лечения'
    #    settingsvar.html = 'https: // www.google.com / search?client = opera & q = Сердечная + недостаточность + тактика + лечения & sourceid = opera & ie = UTF - 8 & oe = UTF - 8'
    #    writediagnoz()
    #    return render(request, settingsvar.html, context=settingsvar.nextstepdata)
    #    return
    settingsvar.html = 'diagnoz/google.html'
    context = {
        'base_url': 'https://www.google.com/search',
        'search_term': settingsvar.url,
    }
    return render(request, settingsvar.html, context)


# --- Перегляд проведених інтервью

def pacientlistinterwiev(request):  # httpRequest
    settingsvar.addinterviewrecept = False
    backpacientlistinterwiev(request)
    return render(request, settingsvar.html, settingsvar.nextstepdata)


def backpacientlistinterwiev(request):
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev' \
            or settingsvar.kabinet == 'likarreceptionpacient'
            or settingsvar.kabinet == 'likarworkdiagnoz'
            or settingsvar.kabinet == 'likarvisitngdays'
            or settingsvar.kabinet == 'likarlibdiagnoz'):
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'pacientlistinterwiev'
        settingsvar.backpage = 'listinterwiev'
        settingsvar.kabinet = 'listinterwiev'
        settingsvar.kabinetitem = 'listinterwiev'
        settingsvar.backurl = funcbakurl()
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            funcshablonlistpacient()
    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pacientlistinterwiev')
    unloadlog(json)
    return


# --- Функція формування шаблону для списку опитувань
def funcshablonlistpacient():
    iduser = funciduser()
    settingsvar.html = 'diagnoz/pacientlistinterwiev.html'
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['likar'] = False
    settingsvar.nextstepdata['backurl'] = settingsvar.backurl

    settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/0/' + settingsvar.kodPacienta, '', 'GET')
    if len(settingsvar.listapi) > 0:
        if settingsvar.funciya == 'checkvisitinglikar':
            settingsvar.kodDoctor = settingsvar.listapi[0]['kodDoctor']
            settingsvar.likar = rest_api('/api/ApiControllerDoctor/' + settingsvar.kodDoctor + '/0/0',
                                         '', 'GET')
            if len(settingsvar.likar) > 0:
                medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '',
                    'GET')
                settingsvar.namemedzaklad = medzaklad['name'] + ' ' + medzaklad['adres']
                settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
                #                settingsvar.mobtellikar = settingsvar.likar['telefon']
                settingsvar.nextstepdata[
                    'piblikar'] = settingsvar.namemedzaklad + 'Лікар : ' + settingsvar.namelikar  # + " " + settingsvar.mobtellikar
        else:
            for item in settingsvar.listapi:
                pacient = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
                if 'name' in pacient:
                    item['resultDiagnoz'] = pacient['name'] + ' ' + pacient['surname'] + ' Телефон: ' + pacient['tel']
                api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
                if len(api) > 0:
                    item['kodDiagnoz'] = api[0]['kodDiagnoz']

            settingsvar.nextstepdata['complaintlist'] = settingsvar.listapi
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return


# --- Запис на обстеження до  лікаря

def pacientreceptionlikar(request):  # httpRequest
    backpacientreceptionlikar(request)
    return render(request, settingsvar.html, settingsvar.nextstepdata)


def backpacientreceptionlikar(request):
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev'
            or settingsvar.kabinet == 'likarreceptionpacient'
            or settingsvar.kabinet == 'likarworkdiagnoz'
            or settingsvar.kabinet == 'likarvisitngdays'
            or settingsvar.kabinet == 'likarlibdiagnoz'):
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.addinterviewrecept = False
        settingsvar.nawpage = 'pacientreceptionlikar'
        settingsvar.kabinet = 'listreceptionlikar'
        settingsvar.kabinetitem = 'listreceptionlikar'
        settingsvar.backurl = funcbakurl()
        settingsvar.backpage = 'listreceptionlikar'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            funcshablonlistreceptionlikar()
    json = ('IdUser: ' + settingsvar.kodPacienta + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: pacientreceptionlikar')
    unloadlog(json)
    return


# --- Функція формування шаблону  переліку дат обстежень пацієнта у лікаря
def funcshablonlistreceptionlikar():
    iduser = funciduser()
    settingsvar.html = 'diagnoz/pacientreceptionlikar.html'
    settingsvar.listAdmissionlikar = []
    diagnoz = []
    PacientName = ""
    settingsvar.receptitem = 'receptprofillmedzaklad'
    shablonpacient(settingsvar.pacient)
    settingsvar.nextstepdata['backurl'] = settingsvar.backurl
    settingsvar.listapi = rest_api('api/RegistrationAppointmentController/' + settingsvar.kodPacienta + '/0/0/0', '',
                                   'GET')
    if len(settingsvar.listapi) > 0:
        stepdata = {}
        doc = rest_api('api/PacientController/' + settingsvar.listapi[0]['kodPacient'] + '/0/0/0/0', '', 'GET')
        if 'name' in doc:
            PacientName = doc['name'] + ' ' + doc['surname'] + ' Телефон: ' + doc['tel']
        for item in settingsvar.listapi:
            if item['dateDoctor'] != '' and item['dateInterview'] != '':
                stepdata = {}
                if len(item['kodDoctor']) > 0:
                    likar = rest_api('/api/ApiControllerDoctor/' + item['kodDoctor'] + "/0/0", '', 'GET')
                    likarName = ' не встановлено'

                    if 'name' in likar:
                        likarName = likar['name'] + likar['surname']  # + " тел.: " + likar['telefon']
                    medzak = {}
                    if 'edrpou' in likar:
                        medzak = rest_api('/api/MedicalInstitutionController/' + likar['edrpou'] + "/0/0/0", '', 'GET')
                    medzaklad = ''
                    if len(medzak) > 0: medzaklad = medzak['name'] + ' ' + medzak['adres']
                    if item['kodDiagnoz'] != None:
                        diagnoz = rest_api('api/DiagnozController/' + item['kodDiagnoz'] + '/0/0', '', 'GET')

                    dateDoctor = item['dateDoctor']
                    nameDiagnoz = " не встановлено"
                    if 'nameDiagnoza' in diagnoz:
                        nameDiagnoz = diagnoz['nameDiagnoza']
                    stepdata['pacient'] = PacientName
                    stepdata['namelikar'] = likarName
                    stepdata['medzaklad'] = medzaklad
                    stepdata['dateInterview'] = item['dateInterview']  # 'Дата опитування: ' +
                    stepdata['dateDoctor'] = item['dateDoctor']  # 'Дата прийому:   ' +dateVizita
                    stepdata['diagnoz'] = nameDiagnoz  # 'Попередній діагноз: ' +
                    stepdata['kodDoctor'] = item['kodDoctor']
                    stepdata['kodProtokola'] = item['kodProtokola']
                    stepdata['kodDiagnoz'] = item['kodDiagnoz']
                    stepdata['id'] = item['id']
                    stepdata['kodPacient'] = settingsvar.kodPacienta
                    settingsvar.listAdmissionlikar.append(stepdata)

        settingsvar.nextstepdata['complaintlist'] = settingsvar.listAdmissionlikar
        settingsvar.listapi = settingsvar.listAdmissionlikar
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні записи про обстеження у лікаря.')
    return


# --- Тиск, пульс, аналізи
def pacientstanhealth(request):  # httpRequest
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev'
            or settingsvar.kabinet == 'likarreceptionpacient'
            or settingsvar.kabinet == 'likarworkdiagnoz'
            or settingsvar.kabinet == 'likarvisitngdays'
            or settingsvar.kabinet == 'likarlibdiagnoz'):
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.listapi = []
        settingsvar.readprofil = False
        settingsvar.backurl = funcbakurl()
        settingsvar.nawpage = 'pacient'
        settingsvar.kabinet = 'pacientstanhealth'
        settingsvar.kabinetitem = 'pacientstanhealth'
        settingsvar.backpage = 'pacientstanhealth'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            funcshablonstanhealth()
            if len(settingsvar.stanhealth) == 0:
                addpulstisk(request)
            else:
                if request.method == 'POST':
                    addpulstisk(request)
    return render(request, settingsvar.html, settingsvar.nextstepdata)


def funcshablonstanhealth():
    iduser = funciduser()
    backurl = funcbakurl()
    PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']
    settingsvar.html = 'diagnoz/pacientstanhealth.html'
    settingsvar.stanhealth = rest_api('api/PacientMapAnalizController/' + settingsvar.kodPacienta + '/0', '', 'GET')
    if len(settingsvar.stanhealth) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.stanhealth,
            'backurl': backurl,
            'pacient': PacientName
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутня інформація.')
    return


# --- Запит на стан злоровья із кабінету лікаря
def stanhealth(request):
    settingsvar.backpage = 'stanhealth'
    funcshablonstanhealth()
    return render(request, settingsvar.html, settingsvar.nextstepdata)


# --- Додати новий рядок показників стану здоровья пульс тиск температура
def pulstisktemp(request):
    settingsvar.readprofil = True
    addpulstisk(request)
    return render(request, settingsvar.html, settingsvar.nextstepdata)


def addpulstisk(request):
    settingsvar.html = 'diagnoz/addpacientpulstisk.html'
    iduser = funciduser()
    if settingsvar.readprofil == True and settingsvar.pacienthealth == False: request.method = 'GET'
    if request.method == 'POST':
        form = ReestrPulsTiskForm(request.POST)
        settingsvar.formaccount = form.data
        if settingsvar.formaccount['pulls'] == None:
            settingsvar.setReestrAccount = False
            errorprofil('Шановний користувач! Пульс не введено')
        else:
            if settingsvar.formaccount['pressure'] == None:
                settingsvar.setReestrAccount = False
                errorprofil('Шановний користувач! Тиск не введено')
            else:
                settingsvar.dateInterview = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                json = {'id': 0,

                        'KodPacient': settingsvar.kodPacienta,
                        'DateAnaliza': settingsvar.dateInterview,
                        'Pulse': settingsvar.formaccount['pulls'],
                        'Pressure': settingsvar.formaccount['pressure'],
                        'Temperature': settingsvar.formaccount['temperature'],
                        'ResultAnaliza': '',
                        }
                settingsvar.listapi = rest_api('/api/PacientMapAnalizController/', json, 'POST')
                funcshablonstanhealth()

    else:
        settingsvar.pacienthealth = True
        formreestraccount = ReestrPulsTiskForm()
        settingsvar.nextstepdata = {
            'form': formreestraccount,
            'backurl': 'pacientstanhealth',
            'iduser': iduser
        }
    return


# --- Таблица аналізов крові по датам
def mapanalizkrovi(request):
    iduser = funciduser()

    settingsvar.backpage = 'mapanalizkrovi'
    PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']
    settingsvar.html = 'diagnoz/pacientmapkrovi.html'
    mapakrovi = rest_api('api/PacientAnalizKroviController/' + settingsvar.kodPacienta + '/0', '', 'GET')
    if len(mapakrovi) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': mapakrovi,
            'pacient': PacientName
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутня інформація.')

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Додати аналіз крові
def addanalizkrovi(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Таблица аналізов сечі по датам
def mapanalizurines(request):
    iduser = funciduser()
    settingsvar.backpage = 'mapanalizurines'
    PacientName = settingsvar.pacient['name'] + ' ' + settingsvar.pacient['surname']
    settingsvar.html = 'diagnoz/pacientmapuries.html'
    mapauries = rest_api('api/PacientAnalizUrineController/' + settingsvar.kodPacienta + '/0', '', 'GET')
    if len(mapauries) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': mapauries,
            'pacient': PacientName
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутня інформація.')

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Додати аналіз сечі
def addanalizuries(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Вибрати сімейного лікаря
def selectfamilylikar(request):
    if (
            settingsvar.kabinet == 'likar' or settingsvar.kabinet == 'likarinterwiev' or settingsvar.kabinet == 'likarlistinterwiev'
            or settingsvar.kabinet == 'likarreceptionpacient'
            or settingsvar.kabinet == 'likarworkdiagnoz'
            or settingsvar.kabinet == 'likarvisitngdays'
            or settingsvar.kabinet == 'likarlibdiagnoz'):
        errorprofil('Для входу до кабінету пацієнта необхідно вийти з кабінету лікаря.')
    else:
        cleanvars()
        settingsvar.listapi = []
        settingsvar.readprofil = False
        settingsvar.backurl = funcbakurl()
        settingsvar.nawpage = 'pacient'
        settingsvar.kabinet = 'selectfamilylikar'
        settingsvar.kabinetitem = 'selectfamilylikar'
        settingsvar.backpage = 'selectfamilylikar'
        if settingsvar.setpost == False:
            accountuser(request)
        else:
            funcselectfamilylikar()
            if len(settingsvar.listlikar) == 0:
                errorprofil('Щановний користувач! За вашим запитом відсутні приписані до вас лікарі.')
    return render(request, settingsvar.html, settingsvar.nextstepdata)


def funcselectfamilylikar():
    settingsvar.backpage = settingsvar.kabinet
    settingsvar.kabinetitem = 'selectfamilylikar'
    settingsvar.receptitem = 'selectfamilylikar'
    settingsvar.html = 'diagnoz/selectlikarprofil.html'
    listfamilylikar()
    selectlikarrofil(settingsvar.listlikar)

    return


def listfamilylikar():
    likarspec = []
    listfamilylikar = rest_api('/api/ControlerFamilyLikar/' + settingsvar.kodPacienta + '/0', '', 'GET')
    if len(listfamilylikar) > 0:
        for item in listfamilylikar:
            settingsvar.likar = rest_api('/api/ApiControllerDoctor/' + item['kodDoctor'] + '/0/0', '', 'GET')
            medzaklad = rest_api('/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '',
                                 'GET')
            item['name'] = settingsvar.likar['name']
            item['surname'] = settingsvar.likar['surname']
            item['kodzaklad'] = settingsvar.likar['edrpou']
            item['specialnoct'] = settingsvar.likar['specialnoct']
            item['zakladname'] = medzaklad['name']
            item['adreszak'] = medzaklad['adres']
            item['tel'] = medzaklad['telefon']
            item['checklikar'] = False
            likarspec.append(item)
    settingsvar.listlikar = likarspec
    return

def addfamilylikar(request):
    settingsvar.backpage = 'addfamilylikar'
    likarspec = []
    settingsvar.likar = rest_api('/api/ApiControllerDoctor/', '', 'GET')
    for item in settingsvar.likar:
        medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '', 'GET')
        item['kodzaklad'] = item['edrpou']
        item['zakladname'] = medzaklad['name']
        item['adreszak'] = medzaklad['adres']
        item['tel'] = medzaklad['telefon']
        likarspec.append(item)
    selectlikarrofil(likarspec)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def likar_checkbox_view(request, select_likar):
    tmp = []
    dellikar = False
    if request.method == 'POST':

        data = json.loads(request.body)
        activ_checkbox = data['active']

        for item in settingsvar.listlikar:
            if item['kodDoctor'] == select_likar:
                if activ_checkbox == True: item['checklikar'] = True
                if activ_checkbox == False: item['checklikar'] = False
            else:
                if 'checklikar' not in item:
                    item['checklikar'] = False
            tmp.append(item)

        for item in tmp:
            if item['checklikar'] == True: dellikar = True
        settingsvar.listlikar = []
        for item in tmp:
            settingsvar.listlikar.append(item)

        request.method = 'GET'
    settingsvar.nextstepdata['detalinglist'] = settingsvar.listlikar
    settingsvar.nextstepdata['dellikar'] = dellikar
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def deletefamilylikar(request):
    tmp = []

    for item in settingsvar.listlikar:
        if item['checklikar'] == True:
            dellikar = rest_api(
                '/api/ControlerFamilyLikar/' + '0/0/' + item['kodDoctor'], '', 'DEL')

    listfamilylikar()
    settingsvar.nextstepdata['detalinglist'] = settingsvar.listlikar
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)



# --------- Лікар
# --- Реєстрація до кабінету лікаря
# ---------   Профіль лікаря

# --- Реєстрація профіля лікаря

def receptprofillikar(request):
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def inputkabinetlikar(request):
    match settingsvar.kabinet:
        case 'pacient' | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth':
            errorprofil('Для входу до кабінету лікаря необхідно вийти з кабінету пацієнта.')
            return False
    return True


# --- Вхід до кабінету  лікаря
def likarprofil(request):  # httpRequest

    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.nawpage = 'likarprofil'
        settingsvar.kabinetitem = 'likar'
        settingsvar.kabinet = 'likarprofil'
        settingsvar.backpage = 'likarprofil'
        if settingsvar.setpostlikar == False:
            accountuser(request)
            settingsvar.initialprofil = True
        else:
            settingsvar.html = 'diagnoz/likarprofil.html'
            if settingsvar.initialprofil == True:
                likarinfoprofil()
            else:
                settingsvar.html = 'diagnoz/likar.html'
                settingsvar.initialprofil = True

    json = ('IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarprofil')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def likarinfoprofil():
    iduser = funciduser()
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'medzaklad': settingsvar.namemedzaklad,
        'name': "Ім'я, прівище  :   " + settingsvar.likar['name'] + " " + settingsvar.likar['surname'],
        'specialnoct': "Спеціальність  :   " + settingsvar.likar['specialnoct'],
        'telefon': "Телефон  :   " + settingsvar.likar['telefon'],
        'email': "Поштова електронна адреса :   " + settingsvar.likar['email'],
        'uriwebDoctor': "Сторінка в інтенеті  :   " + settingsvar.likar['uriwebDoctor'],
        'napryamok': "Робочі напрямки",

    }
    settingsvar.html = 'diagnoz/likarprofil.html'
    return


# Робочі напрямки лікаря щодо діагностування захворювання пацієнта
def likarnapryamok(request):
    settingsvar.directdiagnoz = False
    listworkdiagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# форма для коригування профілю лікаря
def profillikarform(request):
    settingsvar.editprofil = True
    getpostlikarprofil(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def getpostlikarprofil(request):
    settingsvar.html = 'diagnoz/profillikarform.html'
    settingsvar.kabinetitem = 'likarprofil'
    if request.method == 'POST':
        form = LikarForm(request.POST)
        json = {'id': 0,
                'KodDoctor': '',
                'Name': form.data['name'],
                'Surname': form.data['surname'],
                'Telefon': form.data['telefon'],
                'Email': form.data['email'],
                'Edrpou': '',
                'Specialnoct': form.data['specialnoct'],
                'Napryamok': '',
                'UriwebDoctor': form.data['uriwebDoctor'],
                }

        if settingsvar.editprofil == False:
            # --- записати в Бд облікові дані
            if settingsvar.kabinet == 'pacient':
                funcaddaccount(settingsvar.formaccount.data['login'], settingsvar.formaccount.data['password'])
            # --- записати в Бд введенний профіль
            settingsvar.pacient = rest_api('/api/ApiControllerDoctor/', json, 'POST')
        else:
            json['id'] = settingsvar.likar['id']
            json['KodDoctor'] = settingsvar.likar['kodDoctor']
            json['Edrpou'] = settingsvar.likar['edrpou']
            settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
            settingsvar.likar = rest_api('/api/ApiControllerDoctor/', json, 'PUT')
        if len(settingsvar.likar) > 0:
            settingsvar.setpost = True
            settingsvar.setpostlikar = True
            errorprofil('Шановний користувач!  Ваш профіль збережено.')
        else:
            errorprofil('Шановний користувач! Похибка на серевері. Ваш профіль не збережено.')
    else:
        if len(settingsvar.likar) > 0:
            settingsvar.readprofil = False
            settingsvar.editprofil = True
            iduser = funciduser()
            form = LikarForm(initial=settingsvar.likar)
            settingsvar.nextstepdata = {
                'form': form,
                'next': settingsvar.readprofil,
                'backurl': 'likar'
            }
        else:
            form = LikarForm()
            settingsvar.nextstepdata = {
                'form': form,
                'next': False
            }
    return


# --- Функція пошуку пацієнта в БД для проведення опитування
def search_pacient():
    iduser = funciduser()
    backurl = funcbakurl()
    reestr = True
    compl = 'Реєстрація'
    if settingsvar.funciya == 'checkvisitinglikar':
        reestr = False
        iduser = 'Запит про обстеження пацієнта'
    formsearch = SearchPacient()
    settingsvar.nextstepdata = {
        'form': formsearch,
        'compl': compl,
        'iduser': iduser,
        'reestrinput': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
        'medzaklad': settingsvar.namemedzaklad,
        'backurl': backurl,
        'reestr': reestr
    }
    settingsvar.html = 'diagnoz/searchpacient.html'
    return


# --------- Прведення опитування лікарем
def likarinterwiev(request):  # httpRequest
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'likarinterwiev'
        settingsvar.kabinetitem = 'likarinterwiev'
        settingsvar.kabinet = 'likarinterwiev'
        settingsvar.backpage = 'likarinterwiev'
        settingsvar.receptitem = 'likarinterwiev'
        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            # --- пошук даних пацієнта для проведення опитування
            backurl = 'likar'
            if settingsvar.search == False:
                if request.method == 'POST':
                    form = SearchPacient(request.POST)
                    settingsvar.formsearch = form.data
                    request.method = 'GET'
                    funcsearchpacient(request, settingsvar.formsearch)
                    settingsvar.search = True

                else:
                    settingsvar.setpost = False
                    search_pacient()
            else:
                if settingsvar.receptitem != 'receptinterwiev' and settingsvar.receptitem != 'likarinterwiev': request.method = 'GET'
                funcsearchpacient(request, settingsvar.formsearch)
            settingsvar.nextstepdata['backurl'] = backurl
    json = ('IdUser: ' + settingsvar.kabinet + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarinterwiev')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# ---Блок функцій забезпечующих виведення переліку проведених опитувань пацієнтів


# 1. Вхід до кабінету та запит на виведення переліку проведених опитувань пацієнтів
def likarlistinterwiev(request):  # httpRequest
    settingsvar.addinterviewrecept = False
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'profilinterview'
        settingsvar.kabinetitem = 'likarlistinterwiev'
        settingsvar.kabinet = 'likarlistinterwiev'
        settingsvar.backpage = 'likarlistinterwiev'

        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            listlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# 2. Запит до БД за заданим кодом лікаря
def listlikar():
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.backpage = 'likarlistinterwiev'
    settingsvar.nawpage = 'likarlistinterweiv'
    settingsvar.html = 'diagnoz/likarlistinterwiev.html'
    settingsvar.listapi = rest_api('api/ColectionInterviewController/' + '0/' + settingsvar.kodDoctor + '/0', '', 'GET')

    if len(settingsvar.listapi) > 0:
        for item in settingsvar.listapi:
            pacient = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
            if 'name' in pacient:
                item['resultDiagnoz'] = pacient['name'] + ' ' + pacient['surname'] + ' Телефон: ' + pacient['tel']
            api = rest_api('/api/DependencyDiagnozController/' + "0/" + item['kodProtokola'] + "/0", '', 'GET')
            if len(api) > 0:
                item['kodDiagnoz'] = api[0]['kodDiagnoz']

        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом відсутні проведені опитування.')
    return


# --- Розклад обстеження  пацієнтів
def likarreceptionpacient(request):  # httpRequest
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'profilinterview'
        settingsvar.kabinetitem = 'likarreceptionpacient'
        settingsvar.kabinet = 'likarreceptionpacient'
        settingsvar.backpage = 'likarreceptionpacient'
        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            listreceptionpacient(request)
    json = ('IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarreceptionpacient')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listreceptionpacient(request):
    iduser = ""  # funciduser()
    backurl = funcbakurl()
    settingsvar.backpage = 'likarreceptionpacient'
    settingsvar.nawpage = 'likarreceptionpacient'
    settingsvar.html = 'diagnoz/likarreceptionpacient.html'
    funsearchpacientform(request)
    if len(settingsvar.pacientselect) == 0:
        settingsvar.listapi = rest_api('api/ControllerAdmissionPatients/' + '0/' + settingsvar.kodDoctor + '/0/0', '',
                                   'GET')
        if len(settingsvar.listapi) > 0:
            settingsvar.listreception = []
            settingsvar.listprofpacient = []
            for item in settingsvar.listapi:

                if len(item['dateVizita']) > 0:
                    profpacient = rest_api('api/PacientController/' + item['kodPacient'] + '/0/0/0/0', '', 'GET')
                    if len(profpacient) > 0:

                        settingsvar.listprofpacient.append(profpacient)

                        if item['kodDiagnoz'] != None and len(item['kodDiagnoz']) > 0:
                            profdiagnoz = rest_api('api/DiagnozController/' + item['kodDiagnoz'] + '/0/0', '', 'GET')
                            if len(profdiagnoz) > 0:
                                nameDiagnoza = profdiagnoz['nameDiagnoza']
                                kodDiagnoz = item['kodDiagnoz']
                                strreception = {'kodDoctor': item['kodDoctor'],
                                                'kodPacient': item['kodPacient'],
                                                'namePacient': profpacient['name'] + ' ' + profpacient['surname'],
                                                'dateVizita': item['dateVizita'],
                                                'dateInterview': item['dateInterview'],
                                                'kodProtokola': item['kodProtokola'],
                                                'kodDiagnoz': kodDiagnoz,
                                                'nameDiagnoza': nameDiagnoza,
                                                }
                                settingsvar.listreception.append(strreception)

            settingsvar.pacientselect = settingsvar.listreception
            settingsvar.selectbackmeny = False
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'complaintlist': settingsvar.pacientselect,
                'backurl': backurl,
                'piblikar': 'Лікар: ' + settingsvar.likar['name'],  # + " тел.: " + settingsvar.mobtellikar,
                'medzaklad': settingsvar.namemedzaklad,
                'form': settingsvar.formsearchpacient,
            }
        else:
            errorprofil('Шановний користувач! За вашим запитом немає пацієнтів записаних для обстеження  .')
    return


def funsearchpacientform(request):
    if request.method == 'POST':
        form = InputsearchpacientForm(request.POST)
        settingsvar.searchsurname = form.data
        tmp = []
        settingsvar.receptitem = 'InputsearchpacientForm'
        complate = settingsvar.searchsurname['searchpacient'].rstrip()
        for item in settingsvar.listreception:
            if complate.upper() in item['namePacient'].upper():
                tmp.append(item)
        settingsvar.pacientselect = tmp
        settingsvar.nextstepdata['complaintlist'] = tmp
        request.method = 'GET'
        settingsvar.receptitem = 'InputsearchpacientForm'
        settingsvar.selectbackmeny = False
        settingsvar.formsearchpacient = InputsearchpacientForm(initial=settingsvar.searchsurname)
    else:
        if settingsvar.receptitem == 'InputsearchpacientForm': settingsvar.pacientselect = []
        settingsvar.receptitem = 'getsearchpacientForm'
        settingsvar.formsearchpacient = InputsearchpacientForm()

    return

# --- Розклад роботи
def likarvisitngdays(request):  # httpRequest
    if inputkabinetlikar(request) == True:
        if settingsvar.kabinet == "guest":
            listlikarvisitngdays()
        else:
            cleanvars()
            settingsvar.readprofil = False
            settingsvar.nawpage = 'likar'
            settingsvar.kabinetitem = 'likarvisitngdays'
            settingsvar.kabinet = 'likarvisitngdays'
            settingsvar.backpage = 'likarvisitngdays'
            if settingsvar.setpostlikar == False:
                accountuser(request)
            else:
                listlikarvisitngdays()
    json = ('IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarvisitngdays')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listlikarvisitngdays():
    iduser = funciduser()
    backurl = funcbakurl()
    error = False
    errmsg = ''
    profil = ''
    if settingsvar.kabinet == "guest": profil = "guest"
    settingsvar.html = 'diagnoz/likarvisitngdays.html'
    settingsvar.listapi = rest_api('api/ApiControllerVisitingDays/' + settingsvar.kodDoctor + '/0', '', 'GET')
    if len(settingsvar.listapi) == 0:
        error = True
        errmsg = 'Шановний користувач! За вашим запитом не сформовано розклад роботи  .'
    else:
        tmp = []
        for item in settingsvar.listapi:
            if item['onOff'] == 'Так':
                tmp.append(item)
            settingsvar.listapi = tmp
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'complaintlist': settingsvar.listapi,
        'backurl': backurl,
        'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
        'medzaklad': settingsvar.namemedzaklad,
        'error': error,
        'profil': profil,
        'errmsg': errmsg
    }
    return


# Додати розклад прийому пасієнтів
def addvisitingdays(request):
    iduser = funciduser()
    backurl = funcbakurl()
    if request.method == 'POST':
        form = Reestrvisitngdays(request.POST)
        settingsvar.formaccount = form.data

        for key, value in settingsvar.setmonth:
            if key == settingsvar.formaccount['vivsitmonth']:
                numbermonth = value
                break
        time_step = timedelta(minutes=int(settingsvar.formaccount['duration']))
        for itemdays in range(int(settingsvar.formaccount['begindays']), int(settingsvar.formaccount['enddays'])):

            date_format = "%Y-%m-%d %H:%M:%S"
            format_date = "%d.%m.%Y"
            dateyear = datetime.now()
            year = dateyear.year
            date_string = str(year) + "-" + str(numbermonth) + "-" + str(
                itemdays) + " 00:00:00"  # "2023-09-23 00:00:00"
            nawdays = str(itemdays)
            if itemdays < 10: nawdays = "0" + nawdays
            nawmonth = str(numbermonth)
            if numbermonth < 10: nawmonth = "0" + nawmonth
            dateVizita = nawdays + "." + nawmonth + "." + str(year)
            dtvisit = datetime.strptime(dateVizita, format_date)
            ind = dtvisit.weekday()
            if ind != 5 and ind != 6:
                DaysOfTheWeek = settingsvar.storkaweekday[ind]
                if len(settingsvar.formaccount['vivsitweekday']) > 0:
                    if DaysOfTheWeek == settingsvar.formaccount['vivsitweekday']:
                        addvisitingdaypacient(DaysOfTheWeek, date_string, dtvisit, time_step, dateVizita)
                else:
                    addvisitingdaypacient(DaysOfTheWeek, date_string, dtvisit, time_step, dateVizita)

        listlikarvisitngdays()
    else:
        settingsvar.formvisiting = Reestrvisitngdays()
        settingsvar.nextstepdata = {
            'form': settingsvar.formvisiting,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad,

        }
        settingsvar.html = 'diagnoz/addvisitingdays.html'
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Запис поточного рядка  прийому пацієнтів на обстеження
def addvisitingdaypacient(DaysOfTheWeek, date_string, dtvisit, time_step, dateVizita):
    date_format = "%Y-%m-%d %H:%M:%S"
    datework = datetime.strptime(date_string, date_format)
    iso_date = datework.isoformat()
    time_to_add = timedelta(hours=int(settingsvar.formaccount['begintimeofday']))
    time_to_end = timedelta(hours=int(settingsvar.formaccount['endtimeofday']))
    for itemtime in range(int(settingsvar.formaccount['begintimeofday']), 24):
        if time_to_end >= time_to_add:
            datetimebeginvisit = dtvisit + time_to_add
            time_to_add = time_to_add + time_step
            timeVizita = datetimebeginvisit.strftime("%H:%M:%S")
            json = {'id': 0,
                    'KodDoctor': settingsvar.kodDoctor,
                    'DaysOfTheWeek': DaysOfTheWeek,
                    'DateVizita': dateVizita,
                    'TimeVizita': timeVizita,
                    'OnOff': 'Так',
                    'DateWork': iso_date,
                    }
            # --- записати в Бд введенний профіль
            visitingdays = rest_api('/api/VisitingDaysController/', json, 'POST')

    return


# --- Робочі напрямки
def likarworkdiagnoz(request):  # httpRequest
    settingsvar.directdiagnoz = False
    settingsvar.nawpage = 'likarworkdiagnoz'
    settingsvar.kabinetitem = 'likarworkdiagnoz'
    settingsvar.kabinet = 'likarworkdiagnoz'
    settingsvar.backpage = 'likarworkdiagnoz'
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            listworkdiagnoz()
    json = ('IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarworkdiagnoz')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listworkdiagnoz():
    iduser = funciduser()
    backurl = funcbakurl()

    settingsvar.backpage = 'likarworkdiagnoz'
    if settingsvar.kabinet == "guest": settingsvar.backpage = "reception"
    settingsvar.html = 'diagnoz/likarworkdiagnoz.html'
    if settingsvar.directdiagnoz == True:
        settingsvar.listapi = rest_api('api/LikarGrupDiagnozController/', '', 'GET')
        backurl = 'reception'
        listapi()
    else:
        settingsvar.listapi = rest_api('api/LikarGrupDiagnozController/' + settingsvar.kodDoctor + '/0', '', 'GET')
        listapi()
    listapinull = True
    contentnull = 'За вашим запитом не визнвчені напрямки діагностики.'
    if len(settingsvar.listapi) > 0:
        listapinull = False
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listapi,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad,
            'directdiagnoz': settingsvar.directdiagnoz,
            'listapinull': listapinull,
            'сontentnull': contentnull
        }
    return


def listapi():
    tmp = []
    for item in settingsvar.listapi:
        if len(tmp) == 0:
            point = item['icdGrDiagnoz'].index('.')
            item['icd'] = item['icdGrDiagnoz'][0:point]
            tmp.append(item)
        for itemapp in tmp:
            if itemapp['icdGrDiagnoz'] == item['icdGrDiagnoz']:
                app = False
                break
            else:
                app = True
        if app == True:
            point = item['icdGrDiagnoz'].index('.')
            item['icd'] = item['icdGrDiagnoz'][0:point]
            tmp.append(item)
    settingsvar.listapi = tmp
    return


# --- Профільні лікарі

def profillikardiagnoz(request, select_icd):
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.backpage = 'workdiagnozlikar'
    settingsvar.select_icd = select_icd
    settingsvar.gruplikar = []
    compl = 'Перелік спеціалізованих лікарів'
    directdiagnoz = settingsvar.directdiagnoz
    settingsvar.html = 'diagnoz/selectlikarprofil.html'
    workdirection = False
    likar = True
    settingsvar.grupDiagnoz = rest_api('/api/LikarGrupDiagnozController/' + "0/" +
                                       select_icd, '', 'GET')

    for item in settingsvar.grupDiagnoz:
        proflikar = rest_api('/api/ApiControllerDoctor/' + item['kodDoctor'] + "/0/0", '', 'GET')
        if len(proflikar) > 0:
            medzak = rest_api('/api/MedicalInstitutionController/' + proflikar['edrpou'] + "/0/0/0", '', 'GET')
            proflikar['adreszak'] = medzak['adres']
            proflikar['zakladname'] = medzak['name'] + 'Тел.: ' + medzak['telefon']
            settingsvar.gruplikar.append(proflikar)

    point = select_icd[select_icd.rindex('.', 0):]
    reason_url = 'https://www.google.com/search'
    search_reason = point + '+причини+захворювання'
    prof_url = 'https://www.google.com/search'
    search_prof = point + '+профілактика+захворювання'
    medication_url = 'https://www.google.com/search'
    search_medic = point + '+як+лікувати'

    settingsvar.nextstepdata = {
        'iduser': iduser,
        'compl': compl,
        'detalinglist': settingsvar.gruplikar,
        'likar': likar,
        'backurl': backurl,
        'directdiagnoz': directdiagnoz,
        'workdirection': workdirection,
        'namediagnoz': 'Діагноз: ' + settingsvar.select_icd,
        'prof_url': prof_url,
        'search_prof': search_prof,
        'medication_url': medication_url,
        'search_medic': search_medic,
        'reason_url': reason_url,
        'search_reason': search_reason
    }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Профільні заклади
def profillmedzaklad(request, select_icd):
    settingsvar.select_icd = select_icd
    settingsvar.grupmedzaklad = []
    settingsvar.grupDiagnoz = rest_api('/api/MedGrupDiagnozController/' + "0/" +
                                       select_icd + "/0/0", '', 'GET')

    for item in settingsvar.grupDiagnoz:
        if len(item['kodZaklad']) > 0:
            medzaklad = rest_api('/api/MedicalInstitutionController/' + item['kodZaklad'] + '/0/0/0',
                                 '', 'GET')
            if len(settingsvar.grupmedzaklad) == 0: settingsvar.grupmedzaklad.append(medzaklad)
            for itemgrup in settingsvar.grupmedzaklad:
                if itemgrup['kodZaklad'] != item['kodZaklad']:
                    settingsvar.grupmedzaklad.append(medzaklad)
    settingsvar.nawpage = 'backlikarworkdiagnoz'
    settingsvar.backpage = 'profillmedzaklad'
    iduser = funciduser()
    point = select_icd[select_icd.rindex('.', 0):]
    namediagnoz = 'Діагноз : ' + point.replace('.', ' ')

    reason_url = 'https://www.google.com/search'
    search_reason = point + '+причини+захворювання'
    prof_url = 'https://www.google.com/search'
    search_prof = point + '+профілактика+захворювання'
    medication_url = 'https://www.google.com/search'
    search_medic = point + '+як+лікувати'
    settingsvar.html = 'diagnoz/receptionprofilzaklad.html'
    settingsvar.nextstepdata = {
        'iduser': iduser,
        'backurl': 'backlikarworkdiagnoz',
        'compl': 'Перелік профільних медзакладів',
        'detalinglist': settingsvar.grupmedzaklad,
        'piblikar': '',
        'likar': '',
        'namediagnoz': namediagnoz,
        'prof_url': prof_url,
        'search_prof': search_prof,
        'medication_url': medication_url,
        'search_medic': search_medic,
        'reason_url': reason_url,
        'search_reason': search_reason
    }
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backlikarworkdiagnoz(request):
    listworkdiagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Додати робочий напрямок лікаря
def addworkdiagnoz(request):
    iduser = funciduser()
    backurl = 'likarworkdiagnoz'
    settingsvar.html = 'diagnoz/grupdiagnoz.html'
    settingsvar.listGrupDiagnoz = rest_api('api/GrupDiagnozController/', '', 'GET')
    listNameGrDiagnoz()
    if len(settingsvar.listGrupDiagnoz) > 0:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': settingsvar.listGrupDiagnoz,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad,
        }

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listNameGrDiagnoz():
    tmp = []
    for item in settingsvar.listGrupDiagnoz:
        if len(tmp) == 0:
            if '.' in item['nameGrDiagnoz']:
                point = item['nameGrDiagnoz'].index('.')
                item['icd'] = item['nameGrDiagnoz'][0:point]
                tmp.append(item)
        for itemapp in tmp:
            if itemapp['nameGrDiagnoz'] == item['nameGrDiagnoz']:
                app = False
                break
            else:
                app = True
        if app == True:
            if '.' in item['nameGrDiagnoz']:
                point = item['nameGrDiagnoz'].index('.')
                item['icd'] = item['nameGrDiagnoz'][0:point]
                tmp.append(item)
    settingsvar.listGrupDiagnoz = tmp
    return


# Додати новий еапрямок роботи лікаря
def addgrupdiagnoz(request, select_icdGrDiagnoz):
    GrupDiagnoz = rest_api('api/GrupDiagnozController/' + "0/" + select_icdGrDiagnoz, '', 'GET')
    IcdGrDiagnoz = GrupDiagnoz[0]['nameGrDiagnoz']
    json = {'Id': 0,
            'KodDoctor': settingsvar.kodDoctor,
            'IcdGrDiagnoz': IcdGrDiagnoz
            }
    GrupDiagnoz = rest_api('api/LikarGrupDiagnozController/', json, 'POST')
    listworkdiagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# Видалити робочий напрямок лікаря
def deleteworkdiagnoz(request):
    settingsvar.listapi = rest_api('api/LikarGrupDiagnozController/' + settingsvar.select_idigrup + '/0', '',
                                   'DEL')
    listworkdiagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- детелізація переліку  робочих діагнозів за обраним напрямком
def workdiagnozlikar(request, select_kodDoctor, select_icd, select_id):
    settingsvar.select_idigrup = str(select_id)
    settingsvar.select_icd = select_icd
    funcworkdiagnozlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def backworkdiagnozlikar(request):
    funcworkdiagnozlikar()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funcworkdiagnozlikar():
    iduser = funciduser()
    likar = ""
    medzaklad = ""
    backurl = 'likarworkdiagnoz'
    settingsvar.nawpage = 'likarworkdiagnoz'

    if settingsvar.directdiagnoz == False:
        likar = 'Лікар: ' + settingsvar.namelikar  # + " тел.: " + settingsvar.mobtellikar
        medzaklad = settingsvar.namemedzaklad
    else:
        backurl = 'directiondiagnoz'
        settingsvar.nawpage = 'directiondiagnoz'
    settingsvar.backpage = 'workdiagnozlikar'
    settingsvar.html = 'diagnoz/workdiagnozlikar.html'
    settingsvar.listworkdiagnoz = rest_api('api/DiagnozController/' + '0/' + settingsvar.select_icd + '/0', '', 'GET')
    if len(settingsvar.listworkdiagnoz) > 0:
        select_kodDiagnoza = settingsvar.listworkdiagnoz[0]['kodDiagnoza']
        protokol = rest_api('api/DependencyDiagnozController/' + select_kodDiagnoza + "/0/0", '', 'GET')
        workdiagnoz = []
        if len(protokol) > 0:

            for item in protokol:
                prtitem = rest_api('api/InterviewController/' + item['kodProtokola'] + "/0/0/0/0", '', 'GET')
                if len(prtitem) > 0:
                    prtitem['kodDiagnoza'] = select_kodDiagnoza
                    workdiagnoz.append(prtitem)

        if len(workdiagnoz) > 0:

            settingsvar.nextstepdata = {
                'iduser': iduser,
                'complaintlist': workdiagnoz,
                'backurl': backurl,
                'piblikar': likar,
                'medzaklad': medzaklad,
                'icdgrup': settingsvar.listworkdiagnoz[0]['icdGrDiagnoz'],
                'directdiagnoz': settingsvar.directdiagnoz,
                'listnull': False
            }
        else:
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'complaintlist': '',
                'backurl': backurl,
                'piblikar': likar,
                'medzaklad': medzaklad,
                'icdgrup': 'Шановний користувач! За вашим запитом немає робочих діагнозів за ' + settingsvar.select_idigrup,
                'directdiagnoz': settingsvar.directdiagnoz,
                'listnull': True
            }
    else:
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': '',
            'backurl': backurl,
            'piblikar': likar,
            'medzaklad': medzaklad,
            'icdgrup': 'Шановний користувач! За вашим запитом немає робочих діагнозів за ' + settingsvar.select_idigrup,
            'directdiagnoz': settingsvar.directdiagnoz,
            'listnull': True
        }
    return


# формування та виведення  переліку діагнозів за вказаним напрямком
def contentinterview(request, select_kodProtokola):
    backurl = 'backworkdiagnozlikar'
    iduser = funciduser()
    settingsvar.backpage = 'contentinterview'
    settingsvar.html = 'diagnoz/contentinterview.html'
    protokol = rest_api('api/DependencyDiagnozController/' + "0/" + select_kodProtokola + "/0", '', 'GET')
    if len(protokol) > 0:
        workdiagnoz = rest_api('api/ContentInterviewController/' + protokol[0]['kodProtokola'], '', 'GET')
        if len(workdiagnoz) > 0:
            if len(settingsvar.namediagnoz) == 0:
                interwiev = rest_api('api/InterviewController/' + protokol[0]['kodProtokola'] + "/0/0/0/0", '', 'GET')
                if len(interwiev) > 0: settingsvar.namediagnoz = interwiev['nametInterview']
            #           for item in settingsvar.listworkdiagnoz:
            #               if select_kodDiagnoza == item['kodDiagnoza']: settingsvar.namediagnoz = item['nameDiagnoza']
            settingsvar.nextstepdata = {
                'iduser': iduser,
                'listwork': workdiagnoz,
                'medzaklad': settingsvar.namemedzaklad,
                'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
                'namediagnoz': settingsvar.namediagnoz,
                'backurl': backurl

            }
            settingsvar.namediagnoz = ""
        else:
            errorprofil('Шановний користувач! За поточним протоколом відсутній зміст опитування.')
    else:
        errorprofil(
            'Шановний користувач! За поточним кодом протоколу :' + select_kodProtokola + ' відсутній протокол опитування.')
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


# --- Загальна бібліотека напрямків
def likarlibdiagnoz(request):  # httpRequest
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'listlibdiagnoz'
        settingsvar.kabinetitem = 'likarlibdiagnoz'
        settingsvar.kabinet = 'likarlibdiagnoz'

        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            listlibdiagnoz()
    json = ('IdUser: ' + settingsvar.kabinet + ' ' + settingsvar.kodDoctor + ' ' + 'dateseanse :' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ', procedura: likarlibdiagnoz')
    unloadlog(json)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def listlibdiagnoz():
    iduser = funciduser()
    backurl = funcbakurl()
    settingsvar.backpage = 'likarlibdiagnoz'
    settingsvar.html = 'diagnoz/listlibdiagnoz.html'
    libdiagnoz = rest_api('api/DiagnozController/', '', 'GET')
    if len(libdiagnoz) > 0:
        grdiagnoz = ""
        listgrdiagnoz = []
        for item in libdiagnoz:
            if grdiagnoz != item['icdGrDiagnoz']:
                listgrdiagnoz.append(item)
                grdiagnoz = item['icdGrDiagnoz']
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': listgrdiagnoz,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad
        }
    else:
        errorprofil('Шановний користувач! За вашим запитом бібліотека не містить робочі напрямки   .')
    return


def libdiagnoz(request, select_icdGrDiagnoz):
    point = select_icdGrDiagnoz.index('.')
    settingsvar.icdGrDiagnoz = select_icdGrDiagnoz[0:point]
    settingsvar.selecticdGrDiagnoz = select_icdGrDiagnoz
    funclibdiagnoz()
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funclibdiagnoz():
    iduser = funciduser()
    backurl = 'likarlibdiagnoz'
    settingsvar.nawpage = 'listlibdiagnoz'
    settingsvar.backpage = 'libdiagnoz'
    settingsvar.html = 'diagnoz/libdiagnoz.html'
    listworkdiagnoz = rest_api('api/DiagnozController/' + '0/' + settingsvar.icdGrDiagnoz + '/0', '',
                               'GET')
    if len(listworkdiagnoz) > 0:
        tmpworkdiagnoz = []
        for item in listworkdiagnoz:
            protokol = rest_api('api/DependencyDiagnozController/' + item['kodDiagnoza'] + "/0/0", '', 'GET')
            if len(protokol) > 0:
                item['kodProtokola'] = protokol[0]['kodProtokola']
                tmpworkdiagnoz.append(item)
        listworkdiagnoz = tmpworkdiagnoz
        settingsvar.nextstepdata = {
            'iduser': iduser,
            'complaintlist': listworkdiagnoz,
            'backurl': backurl,
            'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
            'medzaklad': settingsvar.namemedzaklad,
            'icdgrup': settingsvar.selecticdGrDiagnoz
        }
    else:
        errorprofil(
            'Шановний користувач! За вашим запитом немає робочих діагнозів за ' + settingsvar.selecticdGrDiagnoz)
        settingsvar.nextstepdata['backurl'] = 'listlibdiagnoz'
    return


def likarinapryamok(request):  # httpRequest
    if inputkabinetlikar(request) == True:
        cleanvars()
        settingsvar.readprofil = False
        settingsvar.nawpage = 'likarinapryamok'
        settingsvar.kabinetitem = 'likarinapryamok'
        settingsvar.kabinet = 'likarinapryamok'
        if settingsvar.backpage != 'likar': settingsvar.backpage = 'likarinapryamok'
        settingsvar.receptitem = 'likarinapryamok'
        if settingsvar.setpostlikar == False:
            accountuser(request)
        else:
            funclikarnapryamok()

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)


def funclikarnapryamok():

    backurl = funcbakurl()
    itemgrupdiagnoz = []
    listworknapryamok = []
    listlikarall = []
    likargrupdiagnoz = rest_api(
        '/api/LikarGrupDiagnozController/' + settingsvar.kodDoctor + "/0", '', 'GET')
    if len(likargrupdiagnoz) > 0:
        for item in likargrupdiagnoz:
            itemgrupdiagnoz = rest_api('/api/LikarGrupDiagnozController/' + "0/" + item['icdGrDiagnoz'], '', 'GET')
            for item in itemgrupdiagnoz:
                listworknapryamok.append(item)

        for item in listworknapryamok:
            CmdStroka = rest_api('/api/ApiControllerDoctor/' + item['kodDoctor'] + "/0/0", '', 'GET')
            doctorfalse = False
            for itemkod in listlikarall:
                if item['kodDoctor'] == itemkod['kodDoctor']:
                    doctorfalse = True
            if doctorfalse == False:
                medzaklad = rest_api('/api/MedicalInstitutionController/' + CmdStroka['edrpou'] + '/0/0/0', '',
                                     'GET')
                CmdStroka['zakladname'] = medzaklad['name']
                CmdStroka['adreszak'] = medzaklad['adres']
                listlikarall.append(CmdStroka)
    else:
        CmdStroka = rest_api('/api/ApiControllerDoctor/' + "0/2/0", '', 'GET')
        # CmdStroka = rest_api('/api/ApiControllerDoctor/'  + "/0/0/0/сімейний", '', 'GET')
        if len(CmdStroka) > 0:
            for item in CmdStroka:
                if item['specialnoct'] == 'сімейний лікар':
                    medzaklad = rest_api('/api/MedicalInstitutionController/' + item['edrpou'] + '/0/0/0', '',
                                         'GET')
                    item['zakladname'] = medzaklad['name']
                    item['adreszak'] = medzaklad['adres']
                    listlikarall.append(item)

    settingsvar.html = 'diagnoz/selectlikarprofil.html'
    settingsvar.nextstepdata = {
        'detalinglist': listlikarall,
        'backurl': backurl,
        'piblikar': 'Лікар: ' + settingsvar.namelikar,  # + " тел.: " + settingsvar.mobtellikar,
        'medzaklad': settingsvar.namemedzaklad,
        'compl': 'Перелік колег лікарів, які працюють за аналочними напрямками',
        'workdirection': True,
        'likarikolegi': True
    }

    return


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
