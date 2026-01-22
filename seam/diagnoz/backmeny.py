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
            if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev' or settingsvar.receptitem == 'getsearchcomplateForm':
                views.funcinterwiev(request)
            else:
                if settingsvar.receptitem == 'reception':
                    views.backreception()
                else:
                    views.writediagnoz()
                    settingsvar.receptitem = 'reception'
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
                    views.listworkdiagnoz()
                case 'selectedprofillikar':
                    views.backreceptprofillmedzaklad(request)

        case "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'pacientinterwiev':

            if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                views.funcinterwiev(request)
                settingsvar.selectbackmeny = True
            else:
                if settingsvar.receptitem == 'getsearchcomplateForm' and settingsvar.selectbackmeny == True:
                    views.funcinterwiev(request)
                    settingsvar.selectbackmeny = False
                else:
                    if settingsvar.receptitem == 'getsearchcomplateForm' and settingsvar.selectbackmeny == False:
                        views.writediagnoz()
                        settingsvar.receptitem = 'pacient'
                    else:
                        views.pacient(request)
        case 'likarinterwiev':
            if settingsvar.receptitem == 'pacientinterwiev':
                views.pacient(request)
            else:
                if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                    views.funcinterwiev(request)
                    # settingsvar.receptitem = 'getsearchcomplateForm'
                else:
                    if settingsvar.receptitem == 'getsearchcomplateForm':
                        views.funcinterwiev(request)
                    else:
                        views.likar(request)
        case "likarprofil" | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':

            if settingsvar.backpage == 'likarreceptionpacient':

                settingsvar.selectbackmeny = True
                views.listreceptionpacient(request)
                if settingsvar.selectbackmeny == True:
                    views.likar(request)
            else:
                views.likar(request)

        case 'receptinterwiev':
            if settingsvar.receptitem == 'InputsearchcomplateForm':  # or settingsvar.receptitem == 'getsearchcomplateForm':
                views.funcinterwiev(request)
            else:
                views.likar(request)

        case 'profilinterview':
            match settingsvar.kabinet:
                case 'guest':
                    settingsvar.search = True
                    views.checkvisitinglikar(request)
                case 'likarlistinterwiev':
                    views.listlikar()
                case 'likarreceptionpacient':
                    views.listreceptionpacient(request)
                case 'listinterwiev':
                    views.backpacientlistinterwiev(request)
                case 'listreceptionlikar':
                    views.backpacientreceptionlikar(request)
        case 'workdiagnozlikar':
            views.listworkdiagnoz()
        case 'contentinterview' | 'contentinterwiev':

            if settingsvar.receptitem == 'interwievcomplaint':
                if settingsvar.kabinet == 'guest':
                    match settingsvar.nawpage:
                        case 'backprofilinterview':
                            # views.backprofilinterview(request)
                            views.saveselectlikar(settingsvar.pacient)
                        case 'backshablonselect':
                            views.shablonselect(request)
                        case _:
                            views.writediagnoz()
                else:
                    views.writediagnoz()
            else:

                if settingsvar.kabinet == 'interwiev' and (
                        settingsvar.receptitem == 'pacientinterwiev' or settingsvar.receptitem == 'getsearchcomplateForm'):
                    if settingsvar.nawpage == 'backfromcontent':
                        views.writediagnoz()
                    else:
                        views.saveselectlikar(settingsvar.pacient)
                else:
                    if settingsvar.receptitem == 'receptinterwiev':
                        views.writediagnoz()
                    else:
                        if settingsvar.receptitem == 'receptprofillmedzaklad':
                            views.backprofilinterview(request)
                        else:
                            if settingsvar.kabinet == 'guest' or settingsvar.kabinet == 'likarworkdiagnoz' or settingsvar.kabinet == 'likarprofil':
                                if settingsvar.kabinet == 'guest' and settingsvar.receptitem == 'getsearchcomplateForm':
                                    views.writediagnoz()
                                else:
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
