from django.shortcuts import render, redirect

from django.http import HttpResponse


def index(request):
    print(request, dir(request))
    return HttpResponse(f"<h1>Public Index {request.user}</h1>")


def callback(request):
    code = request.GET.get("code")
    subdomain = request.GET.get("state")
    host = request.get_host()
    redirect_uri = f"http://{subdomain}.{host}/callback?code={code}"
    return redirect(redirect_uri)
