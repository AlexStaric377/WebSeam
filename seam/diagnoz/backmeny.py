from django.shortcuts import render

from diagnoz import settingsvar
from diagnoz import views


def backpage(request):

    match settingsvar.backpage:
        case 'home_view':
            views.pacient(request)
        case "":
            views.index(request)
        case 'index':
            views.index(request)
        case "pacient":
                views.pacient(request)
                settingsvar.backpage = 'index'
        case 'selectfamilylikar':
            views.pacient(request)
            # views.selectfamilylikar(request)
            settingsvar.backpage = 'index'
        case "likar":
            match settingsvar.receptitem:
                case 'manuallikar':
                    views.likar(request)
                case 'likarinapryamok':
                    if settingsvar.Onlikarinapryamok == False:
                        views.likarinapryamok(request)
                        settingsvar.Onlikarinapryamok = True
                    else:
                        views.likar(request)
                case _:
                    views.index(request)
        case 'reception':
            views.backreception()
        case 'likarinapryamok':
            views.likarinapryamok(request)
            settingsvar.backpage = 'likar'
        case "checkvisitinglikar":
            if settingsvar.html == 'diagnoz/pacientreceptionlikar.html' or settingsvar.html == 'diagnoz/searchpacient.html':
                views.backreception()
            else:
                if settingsvar.receptitem == 'receptprofillmedzaklad':
                    views.backreception()
                else:
                    settingsvar.search = True
                    views.backshablonselect(request)

        case 'interwievcomplaint':
            if (settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev'
                    or settingsvar.receptitem == 'getsearchcomplateForm' or settingsvar.receptitem == 'receptfamilylikar'):
                views.funcinterwiev(request)
            else:
                if settingsvar.receptitem == 'reception' or settingsvar.receptitem == 'likar':
                    views.backreception()
                else:
                    if settingsvar.selectbackmeny == True and settingsvar.receptitem == 'interwievcomplaint':
                        settingsvar.receptitem = 'reception'
                        settingsvar.selectbackmeny = False
                        views.funcinterwiev(request)
                    else:
                        if settingsvar.receptitem == 'replaceproflikar':
                            settingsvar.receptitem = 'reception'
                            settingsvar.selectbackmeny = False
                            views.funcinterwiev(request)
                        else:
                            views.writediagnoz()
                            if settingsvar.selectbackmeny == False and settingsvar.receptitem == 'interwievcomplaint':
                                settingsvar.selectbackmeny = True
        case 'directiondiagnoz':
            views.backreception()
        case 'profillmedzaklad':
            views.directiondiagnoz(request)
        case 'shablonlistlikar':
            views.shablonlistlikar()
        case 'workdiagnozlikar':
            views.listworkdiagnoz()
        case 'likarinapryamok':
            views.likarinapryamok()

        case 'selectdprofillikar':
            match settingsvar.receptitem:
                case 'receptprofillmedzaklad':
                    views.backreceptprofillmedzaklad(request)
                case 'likarworkdirection':
                    views.shablonlistlikar()
                case 'backreceptprofillmedzaklad':
                    views.backreception()
                case 'clinicmedzaklad':
                    views.clinicmedzaklad(request)
                    settingsvar.backpage = 'reception'
                case 'familylikar':
                    if settingsvar.backurl == 'familylikar':
                        views.familylikar(request)
                    else:
                        views.backreception()
                    settingsvar.backurl = 'reception'
                case _:
                    views.profillmedzaklad(request, settingsvar.select_icd)

        case 'guest':
            match settingsvar.receptitem:
                case 'ambulance':
                    views.reception(request)
                case 'headache' | 'krovotecha' | 'singe':
                    views.ambulance(request)
                case 'registrprofil' | 'registrkabinet' | 'applicregulat' | 'manuallikar':
                    views.reception(request)
                    settingsvar.backpage = 'index'
                case 'selectlikarfamily':
                    views.clinicmedzaklad(request)
                    settingsvar.backpage = 'reception'
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
                case 'clinicmedzaklad':
                    views.clinicmedzaklad(request)
                    settingsvar.backpage = 'reception'
                case 'profillikar':
                    if settingsvar.backurl == 'profillikar':
                        views.profillikar(request)
                    else:
                        views.backreception()
                    settingsvar.backurl = 'reception'
                case 'familylikar':
                    if settingsvar.backurl == 'familylikar':
                        views.familylikar(request)
                    else:
                        views.backreception()
                    settingsvar.backurl = 'reception'
                case 'interwievcomplaint':
                    if settingsvar.selectbackmeny == True:
                        settingsvar.selectbackmeny = False
                        views.backreception()
                    else:
                        settingsvar.selectbackmeny = True
                        views.funcinterwiev(request)
                case 'getsearchcomplateForm':
                    views.backreception()
                case 'selectedprofillikar':
                    views.backreceptprofillmedzaklad(request)
                case _:
                    views.index(request)

        case "pacientprofil" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth' | 'pacientinterwiev':

            if settingsvar.receptitem == 'InputsearchcomplateForm' or settingsvar.receptitem == 'receptinterwiev':
                views.funcinterwiev(request)
                settingsvar.selectbackmeny = True
            else:
                if settingsvar.receptitem == 'getsearchcomplateForm' and settingsvar.backpage == 'pacientinterwiev':
                    views.funcinterwiev(request)
                    settingsvar.selectbackmeny = False
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
                    settingsvar.selectbackmeny = False
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
                    CmdStroka = views.rest_api('/api/ApiControllerDoctor/' + settingsvar.kodDoctor + "/0/0", '', 'GET')
                    if 'name' in CmdStroka:
                        settingsvar.namelikar = CmdStroka['name'] + " " + CmdStroka['surname']
                        #        settingsvar.mobtellikar = CmdStroka['telefon']
                        settingsvar.likar = CmdStroka
                        medzaklad = views.rest_api(
                            '/api/MedicalInstitutionController/' + settingsvar.likar['edrpou'] + '/0/0/0',
                            '',
                            'GET')
                        settingsvar.namemedzaklad = medzaklad['name']
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
            if settingsvar.receptitem == 'selectlikarfamily':
                views.saveselectlikar(settingsvar.pacient)
            else:
                if settingsvar.receptitem == 'interwievcomplaint' or settingsvar.receptitem == 'replaceproflikar':
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
