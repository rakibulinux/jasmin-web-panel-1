# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone as djtz
from django.conf import settings

import json

from main.core.smpp import TelnetConnection, HTTPCCM

@login_required
def httpccm_view(request):
    return render(request, "web/content/httpccm.html")

@login_required
def httpccm_view_manage(request):
    args, resstatus, resmessage = {}, 400, _("Sorry, Command does not matched.")
    tc, httpccm = None, None
    if request.POST and request.is_ajax():
        s = request.POST.get("s")
        if s in ['list', 'add', 'delete']:
            tc = TelnetConnection()
            httpccm = HTTPCCM(telnet=tc.telnet)
        if tc and httpccm:
            if s == "list":
                args = httpccm.list()
            elif s == "add":
                httpccm.create(data=dict(
                    cid=request.POST.get("cid"),
                    url=request.POST.get("url"),
                    method=request.POST.get("method"),
                ))
            elif s == "delete":
                args = httpccm.destroy(cid=request.POST.get("cid"))
    if isinstance(args, dict):
        args["status"] = resstatus
        args["message"] = str(resmessage)
    else:
        resstatus = 200
    return HttpResponse(json.dumps(args), status=resstatus, content_type="application/json")