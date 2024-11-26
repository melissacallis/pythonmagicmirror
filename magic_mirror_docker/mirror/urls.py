from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('launch-gui/', views.launch_gui, name='launch_gui'),# Home page
      # Weather page
]


