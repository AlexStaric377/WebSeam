from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from diagnoz import settingsvar
from diagnoz import views


def arh(request):
    login_form = AuthenticationForm()
    settingsvar.html = 'diagnoz/index.html'
    settingsvar.nextstepdata = {'login_form': login_form}
    settingsvar.backpage = 'home_view'
    if request.method == 'POST':
        # Если форма отправлена, обрабатываем данные
        login_form = AuthenticationForm(request, data=request.POST)
        settingsvar.formsearch = login_form.data

        json = "0/" + settingsvar.formsearch['username'] + "/" + settingsvar.formsearch['password'] + '/0'
        Stroka = views.rest_api('/api/AccountUserController/' + json, '', 'GET')
        if 'idStatus' in Stroka:
            match Stroka['idStatus']:
                case '1':  # 1- адміністратор,
                    settingsvar.setpost = True
                case '2':  # 2- пацієнт,
                    settingsvar.kodPacienta = Stroka['idUser']
                    settingsvar.pacient = views.rest_api(
                        '/api/PacientController/' + settingsvar.kodPacienta + '/0/0/0/0', '', 'GET')
                    if len(settingsvar.pacient) > 0:
                        settingsvar.setpost = True
                        settingsvar.readprofil = True
                        settingsvar.setpostlikar = True
                        settingsvar.html = 'diagnoz/pacient.html'
                case '3' | '4' | '5':  # 3- лікар, 2 - лікар адміністратор, 5- резерв

                    settingsvar.kodLikar = Stroka['idUser']
                    settingsvar.likar = views.rest_api('/api/ApiControllerDoctor/' + settingsvar.kodLikar + '/0/0',
                                                       '', 'GET')
                    if 'kodDoctor' in settingsvar.likar:
                        settingsvar.kodDoctor = settingsvar.likar['kodDoctor']
                        medzaklad = views.rest_api(
                            '/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0', '',
                            'GET')
                        settingsvar.namemedzaklad = medzaklad['name']
                        settingsvar.namelikar = settingsvar.likar['name'] + ' ' + settingsvar.likar['surname']
                        settingsvar.mobtellikar = settingsvar.likar['telefon']
                        settingsvar.setpost = True
                        settingsvar.readprofil = True
                        settingsvar.setpostlikar = True
                        settingsvar.html = 'diagnoz/likar.html'
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
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
        #        login_form = AuthenticationForm()
        # ----- Добавляем класс 'form-control' для полей -----
        # Это простой способ добавить Bootstrap-стили без crispy-forms
        login_form.fields['username'].widget.attrs.update({'class': 'form-control'})
        login_form.fields['password'].widget.attrs.update({'class': 'form-control'})
        # ---------------------------------------------------
        if settingsvar.kabinet != '': views.exitkab()

    return
