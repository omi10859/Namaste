from django.shortcuts import render

# Create your views here.

def page_not_found(request, **kwargs):
    return render(request, '404.html')

def server_error(request, **kwargs):
    return render(request, '500.html')

def permission_denied(request, **kwargs):
    return render(request, '403.html', {'kwargs': kwargs})

def bad_request(request, **kwargs):
    return render(request, '400.html')