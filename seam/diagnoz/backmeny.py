from django.shortcuts import render

from diagnoz import settingsvar
from diagnoz import views


# def backpage(request):
#    views.exitkab()
#    settingsvar.html = settingsvar.backpage  # 'diagnoz/index.html'
#    settingsvar.nextstepdata = {
#        'mainbar': True}
#    return render(request, settingsvar.html, context=settingsvar.nextstepdata)

def backpage(request):
    views.exitkab()
    match settingsvar.backpage:
        case 'index':
            views.index()
        case "checkvisitinglikar" | 'interwievcomplaint' | 'directiondiagnoz' | 'receptprofillmedzaklad':
            views.backreception()

        case 'guest':

            if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'directiondiagnoz':
                views.listworkdiagnoz()
            if settingsvar.directdiagnoz == True and settingsvar.receptitem == 'receptprofillmedzaklad':
                views.backreceptprofillmedzaklad(request)
        case "pacient" | 'interwiev' | 'listinterwiev' | 'listreceptionlikar' | 'pacientstanhealth':
            views.pacient(request)
        case "likar" | 'likarinterwiev' | 'likarlistinterwiev' | 'likarreceptionpacient' | 'likarworkdiagnoz' | 'likarvisitngdays' | 'likarlibdiagnoz':
            views.likar(request)
        case "likarprofil":
            views.likarprofil(request)

    #    settingsvar.html = settingsvar.backpage  # 'diagnoz/index.html'
    settingsvar.nextstepdata['mainbar'] = True
    return render(request, settingsvar.html, context=settingsvar.nextstepdata)