from django.shortcuts import render

def index(request):
    # Carga el archivo HTML y renderiza la página
    return render(request, 'supermerengones/index.html')