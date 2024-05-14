from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, 'login-page.html')

#def logout(request):
    
def signup(request):
    return render(request, 'signup-page.html')