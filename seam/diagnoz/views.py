from django.shortcuts import render


def index(request):  # httpRequest
    return render(request, 'diagnoz/index.html')


def reception(request):  # httpRequest
    return render(request, 'diagnoz/reception.html')


def pacient(request):  # httpRequest
    return render(request, 'diagnoz/pacient.html')


def likar(request):  # httpRequest
    return render(request, 'diagnoz/likar.html')


def admin(request):  # httpRequest
    return render(request, 'diagnoz/admin.html')


def receptinterwiev(request):  # httpRequest
    return render(request, 'diagnoz/receptinterwiev.html')


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
