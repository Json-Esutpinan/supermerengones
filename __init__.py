from django.shortcuts import render

def index(request):
    # CAMBIAR a 'supermerengones/base.html' para que cargue la plantilla base
    # Y luego la plantilla base debería cargar el index.html
    return render(request, 'supermerengones/base.html')