import json

import environ
import pyodbc
import requests
from django.shortcuts import render
from django.views.generic import ListView

from diagnoz import settingsvar
from .models import Complaint


def rest_api(api_url):
    env = environ.Env()
    urls_api = env('urls_api')
    urls = urls_api + api_url
    response = requests.get(urls)
    return json.loads(response.content)

def index(request):  # httpRequest
    return render(request, 'diagnoz/index.html')


def reception(request):  # httpRequest
    return render(request, 'diagnoz/reception.html')


def pacient(request):  # httpRequest
    return render(request, 'diagnoz/pacient.html')


def likar(request):  # httpRequest
    return render(request, 'diagnoz/likar.html')


def setings(request):  # httpRequest
    return render(request, 'diagnoz/setings.html')


class InterwievListview(ListView):
    model = Complaint
    template_name = 'diagnoz/receptinterwiev.html'
    context_object_name = 'complaintlist'
    list = rest_api('api/ApiControllerComplaint/')
    extra_context = {
        'complaintlist': rest_api('api/ApiControllerComplaint/')
    }


def get_absolute_url(self):
    return reverse('nextquation', args=[str(self.keyComplaint)])


def nextfeature(request, nextfeature_keyComplaint, nextfeature_name):
    settingsvar.feature_name = nextfeature_name
    data = {
        'compl': nextfeature_name,
        'featurelist': rest_api('api/FeatureController/' + "0/" + nextfeature_keyComplaint + "/0/")
    }
    return render(request, 'diagnoz/nextfeature.html', context=data)


def featurespisok(request, featurespisok_keyComplaint, featurespisok_keyFeature):
    settingsvar.spisokfeature.append(featurespisok_keyFeature)

    data = {
        'compl': settingsvar.feature_name,
        'featurelist': rest_api('api/FeatureController/' + "0/" + featurespisok_keyComplaint + "/0/")
    }
    return render(request, 'diagnoz/nextfeature.html', context=data)


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


def contentinterwiev(request):  # httpRequest
    return render(request, 'diagnoz/contentinterwiev.html')


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
