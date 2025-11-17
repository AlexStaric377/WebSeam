from django.shortcuts import render

from diagnoz import settingsvar
from diagnoz import views


def backpage(request):
    #    views.exitkab()
    match settingsvar.backpage:
        case "":
            views.index(request)
        case 'index' | "pacient" | "likar":
            views.index(request)

        case "checkvisitinglikar":
            if settingsvar.html != 'diagnoz/pacientreceptionlikar.html':
                settingsvar.search = True
                views.backshablonselect(request)
            else:
                views.backreception()
        case 'interwievcomplaint' | 'directiondiagnoz':
            views.backreception()
        case 'profillmedzaklad':
            views.directiondiagnoz(request)
        case 'guest':
            match settingsvar.receptitem:
                case 'directiondiagnoz':
                    views.listworkdiagnoz()
                case 'likarworkdiagnoz':
                    views.shablonlistlikar()
                case 'receptprofillmedzaklad':
                    views.backreception()
                case 'selectedprofillikar':
                    views.backreceptprofillmedzaklad(request)

        case "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'pacientinterwiev':
            views.pacient(request)
        case "likarprofil" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            views.likar(request)
    #        case 'likarprofil':
    #            views.likarprofil(request)

    return render(request, settingsvar.html, context=settingsvar.nextstepdata)