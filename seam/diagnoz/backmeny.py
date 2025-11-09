from django.shortcuts import render

from diagnoz import settingsvar
from diagnoz import views


def backpage(request):
    #    views.exitkab()
    match settingsvar.backpage:
        case 'index' | "pacient" | "likar":
            views.index(request)
        case "checkvisitinglikar" | 'interwievcomplaint' | 'directiondiagnoz' | 'receptprofillmedzaklad':
            views.backreception()
        case 'guest':
            if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'directiondiagnoz':
                views.listworkdiagnoz()
            if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'receptprofillmedzaklad':
                views.backreceptprofillmedzaklad(request)
        case "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'pacientinterwiev':
            views.pacient(request)
        case "likarprofil" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            views.likar(request)
    #        case 'likarprofil':
    #            views.likarprofil(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)