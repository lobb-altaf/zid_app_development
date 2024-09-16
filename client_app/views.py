from django.shortcuts import render, redirect

from django.http import HttpResponse

from oauth.models import ZidUser


def index(request):
    print(request, dir(request))

    try:
        sd = ZidUser.objects.get(django_user=request.user)
    except ZidUser.DoesNotExist:
        sd = None

    return HttpResponse(f"<h1> Django {request.user} Zid    {sd}       Index</h1>")


# def create_employee(request):
#     if request.POST:
#         name = request.POST.get("name")
#         employee = Employee(name=name)
#         employee.save()
#         return redirect("client_index")
