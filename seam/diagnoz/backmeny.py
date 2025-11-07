import requests
from django.shortcuts import render
from diagnoz import settingsvar
from diagnoz import views


def backpage(request):
    views.exitkab()
    settingsvar.html = settingsvar.backpage  # 'diagnoz/index.html'
    settingsvar.nextstepdata = {
        'mainbar': True}
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)
