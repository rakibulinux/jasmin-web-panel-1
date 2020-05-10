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

from main.core.smpp import TelnetConnection, Users

@login_required
def users_view(request):
    return render(request, "web/content/users.html")

@login_required
def users_view_manage(request):
    args, resstatus, resmessage = {}, 400, _("Sorry, Command does not matched.")
    tc, users = None, None
    if request.POST and request.is_ajax():
        s = request.POST.get("s")
        if s in ['list', 'add', 'edit', 'delete', 'enable', 'disable', 'smpp_unbind', 'smpp_ban']:
            tc = TelnetConnection()
            users = Users(telnet=tc.telnet)
        if tc and users:
            if s == "list":
                args = users.list()
            elif s == "add":
                users.create(data=dict(
                    uid=request.POST.get("uid"),
                    gid=request.POST.get("gid"),
                    username=request.POST.get("username"),
                    password=request.POST.get("password"),
                ))
            elif s == "edit":
                data = [
                    ["uid", request.POST.get("uid")],
                    ["gid", request.POST.get("gid")],
                    ["username", request.POST.get("username")],
                    ["mt_messaging_cred", "valuefilter", "priority", request.POST.get("priority_f", "^[0-3]$")],
                    ["mt_messaging_cred", "valuefilter", "content", request.POST.get("content_f", ".*")],
                    ["mt_messaging_cred", "valuefilter", "src_addr", request.POST.get("src_addr_f", ".*")],
                    ["mt_messaging_cred", "valuefilter", "dst_addr", request.POST.get("dst_addr_f", ".*")],
                    ["mt_messaging_cred", "valuefilter", "validity_period", request.POST.get("validity_period_f", "^\\d+$")],
                    ["mt_messaging_cred", "defaultvalue", "src_addr", request.POST.get("src_addr_d", "None")],
                    ["mt_messaging_cred", "quota", "http_throughput", request.POST.get("http_throughput", "ND")],
                    ["mt_messaging_cred", "quota", "balance", request.POST.get("balance", "ND")],
                    ["mt_messaging_cred", "quota", "smpps_throughput", request.POST.get("smpps_throughput", "ND")],
                    ["mt_messaging_cred", "quota", "early_percent", request.POST.get("early_percent", "ND")],
                    ["mt_messaging_cred", "quota", "sms_count", request.POST.get("sms_count", "ND")],
                    ["mt_messaging_cred", "authorization", "dlr_level", "True" if request.POST.get("dlr_level", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_long_content", "True" if request.POST.get("http_long_content", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_send", "True" if request.POST.get("http_send", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_dlr_method", "True" if request.POST.get("http_dlr_method", True) else "False"],
                    ["mt_messaging_cred", "authorization", "validity_period", "True" if request.POST.get("validity_period", True) else "False"],
                    ["mt_messaging_cred", "authorization", "priority", "True" if request.POST.get("priority", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_bulk", "True" if request.POST.get("http_bulk", False) else "False"],
                    ["mt_messaging_cred", "authorization", "src_addr", "True" if request.POST.get("src_addr", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_rate", "True" if request.POST.get("http_rate", True) else "False"],
                    ["mt_messaging_cred", "authorization", "http_balance", "True" if request.POST.get("http_balance", True) else "False"],
                    ["mt_messaging_cred", "authorization", "smpps_send", "True" if request.POST.get("smpps_send", True) else "False"],
                ]
                password = request.POST.get("password", "")
                if len(password) > 0:
                    data.append(["password", password])
                users.partial_update(data, uid=request.POST.get("uid"))
            elif s == "delete":
                args = users.destroy(uid=request.POST.get("uid"))
            elif s == "enable":
                args = users.enable(uid=request.POST.get("uid"))
            elif s == "disable":
                args = users.disable(uid=request.POST.get("uid"))
            elif s == "smpp_unbind":
                args = users.smpp_unbind(uid=request.POST.get("uid"))
            elif s == "smpp_ban":
                args = users.smpp_ban(uid=request.POST.get("uid"))
    if isinstance(args, dict):
        args["status"] = resstatus
        args["message"] = str(resmessage)
    else:
        resstatus = 200
    return HttpResponse(json.dumps(args), status=resstatus, content_type="application/json")