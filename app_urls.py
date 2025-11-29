from django.urls import path
from views import index 

urlpatterns = [
    # Esta ruta llama a la función index
    path('', index, name='index'), 
]