# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.http import HttpResponse
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template import Template
from django.template.loader import get_template

from lizard_portal.models import PortalConfiguration


def site(request, application_name, active_tab_name):
    """
        returns html page which loads specified (ext-js) application
    """

    app_javascript_file = get_template('application/'+application_name+'.js')
    #django.template.TemplateDoesNotExist
    t = get_template('portal_pageframe.html')
    c = RequestContext(request, {
            'application': application_name,
            'active_tab': active_tab_name
        })

    return HttpResponse(t.render(c),
        mimetype='text/html')

def application(request, application_name, active_tab_name):
    """
        returns html page which loads specified (ext-js) application
    """

    t = get_template('application/'+application_name+'.js')
    c = RequestContext(request, {
            'application': application_name,
            'active_tab': active_tab_name
        })

    return HttpResponse(t.render(c),
        mimetype='text/javascript')


def json_configuration(request):
    """
    Return JSON for request.
    """
    c = RequestContext(request)

    portal_template = request.GET.get('portalTemplate', 'homepage')

    if request.user.is_authenticated():
        try:
            t = get_template('portals/'+portal_template+'.js')
        except TemplateDoesNotExist, e:
            pc = PortalConfiguration.objects.filter(slug=portal_template)[0]
            t = Template(pc.configuration)
    else:
        t = get_template('portals/geen_toegang.js')

    return HttpResponse(t.render(c),  mimetype="text/plain")


def feature_info(request):
    """
    Return JSON for request.
    """
    url = request.GET.get('request', None)

    import httplib

    urls = url.strip('"').strip("'").strip('http://')

    split = urls.find('/')


    conn = httplib.HTTPConnection(urls[:split])
    conn.request('GET', urls[split:])
    resp = conn.getresponse()

    content =  resp.read()
    return HttpResponse(content,  mimetype="text/plain")
