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
        case 'reception':
            views.backreception()
        case "checkvisitinglikar":
            if settingsvar.html == 'diagnoz/pacientreceptionlikar.html' or settingsvar.html == 'diagnoz/searchpacient.html':
                views.backreception()
            else:
                settingsvar.search = True
                views.backshablonselect(request)

        case 'interwievcomplaint':
            if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                views.funcinterwiev(request)
            else:
                views.backreception()
        case 'directiondiagnoz':
            views.backreception()
        case 'profillmedzaklad':
            views.directiondiagnoz(request)
        case 'shablonlistlikar':
            views.shablonlistlikar()
        case 'workdiagnozlikar':
            views.listworkdiagnoz()
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
            if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                views.funcinterwiev(request)
            else:
                views.pacient(request)
        case 'likarinterwiev':
            if settingsvar.receptitem == 'pacientinterwiev':
                views.pacient(request)
            else:
                if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                    views.funcinterwiev(request)
                else:
                    views.likar(request)
        case "likarprofil" | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            views.likar(request)
        case 'receptinterwiev':
            views.funcinterwiev(request)

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

            if settingsvar.receptitem == 'interwievcomplaint' and settingsvar.nawpage != 'backshablonselect':
                views.writediagnoz()
            else:

                if settingsvar.receptitem == 'pacientinterwiev' and settingsvar.kabinet == 'interwiev':
                    if settingsvar.nawpage == 'backfromcontent':
                        views.writediagnoz()
                    else:
                        views.saveselectlikar(settingsvar.pacient)
                else:
                    if settingsvar.receptitem == 'receptinterwiev':
                        views.writediagnoz()
                    else:
                        if settingsvar.kabinet == 'guest' and settingsvar.nawpage == 'backshablonselect':
                            views.shablonselect(request)
                        else:
                            if settingsvar.kabinet == 'guest' and settingsvar.nawpage == 'backprofilinterview':
                                views.backprofilinterview(request)
                            else:
                                if settingsvar.kabinet == 'guest' or settingsvar.kabinet == 'likarworkdiagnoz' or settingsvar.kabinet == 'likarprofil':
                                    views.backworkdiagnozlikar(request)
                                else:
                                    if settingsvar.kabinet == 'likarinterwiev':
                                        views.saveselectlikar(settingsvar.pacient)
                                    else:
                                        if settingsvar.kabinet == 'likarlibdiagnoz':
                                            views.funclibdiagnoz()
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
