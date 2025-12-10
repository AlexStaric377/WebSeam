from django.shortcuts import render

from diagnoz import settingsvar
from diagnoz import views


def backpage(request):
    #    views.exitkab()
    match settingsvar.backpage:
        case 'home_view':
            views.pacient(request)
        case "":
            views.index(request)
        case 'index' | "pacient" | "likar":
            views.index(request)

        case "checkvisitinglikar":
            if settingsvar.html == 'diagnoz/pacientreceptionlikar.html' or settingsvar.html == 'diagnoz/searchpacient.html':
                views.backreception()
            else:
                settingsvar.search = True
                views.backshablonselect(request)

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
                case 'likarworkdirection':
                    views.shablonlistlikar()
                case 'receptprofillmedzaklad':
                    views.backreceptprofillmedzaklad(request)
                case 'backreceptprofillmedzaklad':
                    views.backreception()
                case 'interwievcomplaint':
                    views.backreception()
                case 'selectedprofillikar':
                    views.backreceptprofillmedzaklad(request)

        case "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'pacientinterwiev':
            views.pacient(request)
        case "likarprofil" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            views.likar(request)
        case 'receptinterwiev':
            views.interwievcomplaint(request)

        case 'profilinterview':
            match settingsvar.kabinet:
                case 'guest':
                    settingsvar.search = True
                    views.checkvisitinglikar(request)
                case 'likarlistinterwiev':
                    views.listlikar()
                case 'likarreceptionpacient':
                    views.listreceptionpacient()
                case 'listinterwiev':
                    views.backpacientlistinterwiev(request)
                case 'listreceptionlikar':
                    views.backpacientreceptionlikar(request)
        case 'workdiagnozlikar':
            views.listworkdiagnoz()
        case 'contentinterview' | 'contentinterwiev':
            if settingsvar.kabinet == 'guest' or settingsvar.kabinet == 'likarworkdiagnoz' or settingsvar.kabinet == 'likarprofil':
                views.backworkdiagnozlikar(request)
            else:
                views.backprofilinterview(request)
        case 'libdiagnoz':
            views.listlibdiagnoz()
        case 'mapanalizkrovi' | 'stanhealth':
            if settingsvar.kabinet == 'pacientstanhealth':
                views.pacientstanhealth(request)
            else:
                views.backprofilinterview(request)
        case 'mapanalizurines':
            if settingsvar.kabinet == 'pacientstanhealth':
                views.pacientstanhealth(request)
            else:
                views.backprofilinterview(request)
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)