from django.shortcuts import render, redirect

from django.http import HttpResponse


def index(request):
    print(request, dir(request))

    return HttpResponse(f"<h1>{request.user} Index</h1>")


# def create_employee(request):
#     if request.POST:
#         name = request.POST.get("name")
#         employee = Employee(name=name)
#         employee.save()
#         return redirect("client_index")
