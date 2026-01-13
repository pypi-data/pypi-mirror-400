from django import template as django_template
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from html import escape
from pathlib import Path

from urllib3 import HTTPResponse

def get_all_templates_files():
    dirs = []
    for engine in django_template.loader.engines.all():
        dirs.extend(engine.template_dirs)
    files = []
    for dir in dirs:
        files.extend(x for x in Path(dir).glob('**/*.html') if x)
        files.extend(x for x in Path(dir).glob('**/*.txt') if x)
    return files

def sanitize_path(filename):
    split_filename = filename.split("templates")
    if len(split_filename) == 1:
        return filename
    else:
        return split_filename[len(split_filename)-1]

def BrandingViewset(request, parameters=False):
    template_files = get_all_templates_files()
    overwrites = []
    html = "<style>pre{white-space: pre-wrap;}</style><div class='text-left padding-large'><h1>DjangoLDP Branding - <small>"
    html += _("Templates registry")
    html += "</small></h1><p>"
    html += _("When two templates share the same name, the first to appear on this list will be the one used")
    html += "</p>"
    status = False
    use_template = True
    for file in template_files:
        filename = sanitize_path(str(file))
        if filename not in overwrites:
            if "djangoldp_branding" in str(file):
                if not status:
                    html += "<div><b style='color: blue;'>"
                    html += _("MANAGED")
                    html += "</b>: "
                else:
                    html += "<div><b style='color: blue;'>"
                    html += _("EXIST")
                    html += "</b>, "
                    html += _("but")
                    html += " <b style='color: red;'>"
                    html += _("UNMANAGED")
                    html += "</b>: "
                    if filename == "/base.html":
                        use_template = False
                overwrites.append(filename)
                html += "<i>%s</i>" % filename
                if "djangoldp_branding" not in str(file):
                    with open(file) as f:
                        html += "<pre>%s</pre>" % escape(f.read())
                html += "</div>"
            elif "/admin/" not in filename or parameters == "with-admin":
                status = True
                html += "<div><b style='color: red;'>"
                html += _("UNMANAGED")
                html += "</b>: "
                html += "<i>%s</i>" % filename
                if "djangoldp_branding" not in str(file):
                    with open(file) as f:
                        html += "<pre>%s</pre>" % escape(f.read())
                html += "</div>"
    html += "</div>"
    if use_template:
        return render(request, 'base.html', {'content': html, 'title': 'Templates Registry'})
    return HttpResponse(html)
